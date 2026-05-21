from bpmn_core import bpmn_diagram, bpmn_elements
import os
from re import sub

# TODO: 
# Break code into more functions / files?
# ^ Further simplify / rewrite -> object oriented
# Correct problem file names
# Fix Missing actions
# type hint list returns
# Standardize qouations
# use types in the pddl - element type they inherent from
# pddl formatting (spaces between predicates, space after action sub sections), type hint predicates
# objects / redo the predicates

class BPMNExporter:

    def __init__(self, diagram: bpmn_diagram.Diagram):
        self.diagram = diagram

    def clean_label(self, label: str) -> str:
        return sub(r'[^a-zA-Z0-9_]', '_', label)
    
    def is_valid_message_flow(self, source: bpmn_elements.Element, target: bpmn_elements.Element):
        if not source or not target:
            return False
        
        return (source.is_task() and target.is_event()) or (source.is_event() and target.is_task())
    
    def get_immediate_preconditions(self, element_id: str, start_events: list[bpmn_elements.Event], get_outgoing, get_incoming, elements_by_id):
        preconditions = set()
        sources = get_incoming(element_id)

        for src_id in sources:
            src_elem = elements_by_id.get(src_id)
            if not src_elem:
                continue

            if src_elem.type == 'exclusiveGateway':
                preconditions.add(f'{element_id}')

            elif src_elem.type == 'inclusiveGateway' and len(get_outgoing(src_id)) > 1:
                branch_pred = f'branch_started_{src_id}_{element_id}'

                preconditions.add(f'({branch_pred})')
                preconditions.add(f'({element_id})')

            elif src_elem.is_event() or src_elem.is_gateway():
                preconditions.add(f'({src_id})')

            else:
                preconditions.add(f'({element_id})')

        if not preconditions and len(start_events) == 1:
            preconditions.add(f'({start_events[0].element_id})')

        return preconditions
    
    def get_unique_action_name(self, base: str, used_action_names) -> str:
        count = used_action_names.get(base, 0)

        if count == 0:
            used_action_names[base] = 1
            return base
        
        else:
            used_action_names[base] += 1
            return f'{base}_{used_action_names[base]}'
        
    def get_effects_with_following_gateways(self, target_ids: list[str], get_outgoing, elements_by_id) -> list[str]:
        effects = []

        for target_id in target_ids:
            branch_effects = {f'({target_id})'}
            target_elem = elements_by_id.get(target_id)

            if target_elem and target_elem.is_event():
                for next_id in get_outgoing(target_id):
                    next_elem = elements_by_id.get(next_id)

                    if next_elem and next_elem.is_gateway():
                        branch_effects.add(f'({next_elem.element_id})')

            if len(branch_effects) == 1:
                effects.append(next(iter(branch_effects)))

            else:
                effects.append(f"(and {' '.join(branch_effects)})")

        return effects

    def get_parallel_gateway_precondition(self, element_id: str, parallel_converging_gatways: set, get_outgoing) -> str:
        for target_id in get_outgoing(element_id):
            if target_id in parallel_converging_gatways:
                counter, incoming_count = parallel_converging_gatways[target_id]

                if counter >= incoming_count:
                    return ""
                    
                predicate = f'\t({target_id}_precondition_{counter})'
                parallel_converging_gatways[target_id][0] += 1

                return predicate
            
        return ""
    
    def map_inclusive_gateway_pairs(self, start_events: list[bpmn_elements.Event], get_outgoing, get_incoming, elements_by_id) -> dict:
        result = {}

        for start_event in start_events:
            visited = set()
            stack = []
            queue = [start_event.element_id]

            while queue:
                cur_id = queue.pop(0)
                cur_elem = elements_by_id.get(cur_id)

                if cur_id in visited or not cur_elem:
                    continue

                visited.add(cur_id)

                if cur_elem.type == 'inclusiveGateway':
                    n_incoming = len(get_incoming(cur_id))
                    n_outgoing = len(get_outgoing(cur_id))

                    if n_incoming == 1 and n_outgoing > 1:
                        stack.append(cur_id)

                    elif n_incoming > 1 and n_outgoing == 1:
                        if stack:
                            diverging_id = stack.pop()
                            converging_id = cur_id

                            result[diverging_id] = converging_id
                            result[converging_id] = diverging_id

                for target in get_outgoing(cur_id):
                    if target not in visited:
                        queue.append(target)

        return result
    
    def generate_inclusive_counter_actions(self, element_id: str, n: int) -> str:
        inc_pred = f'increase_{element_id}'
        dec_pred = f'decrease_{element_id}'
        lines = []

        lines.append(f'\t(:action inclusive_increase_{element_id}')
        lines.append(f'\t\t:parameters ()')
        lines.append(f'\t\t:precondition (and ({inc_pred}))')
        lines.append('\t\t:effect (and')
        lines.append(f'\t\t\t(not ({inc_pred}))')

        for i in reversed(range(n)):
            lines.append(f'\t\t\t(when (inclusive_counter_{element_id}_{i}) (and (not (inclusive_counter_{element_id}_{i})) (inclusive_counter_{element_id}_{i + 1})))')
        
        lines.append('\t\t)')
        lines.append('\t)\n')

        lines.append(f'\t(:action inclusive_decrease_{element_id}')
        lines.append(f'\t\t:parameters ()')
        lines.append(f'\t\t:precondition (and ({dec_pred}))')
        lines.append(f'\t\t:effect (and')
        lines.append(f'\t\t\t(not ({dec_pred}))')

        for i in range (1, n + 1):
            lines.append(f'\t\t\t(when (inclusive_counter_{element_id}_{i}) (and (not (inclusive_counter_{element_id}_{i})) (inclusive_counter_{element_id}_{i - 1})))')

        lines.append('\t\t)')
        lines.append('\t)\n')

        return '\n'.join(lines)
    
    def create_pddl(self):
        pddl_domain, predicates, start_events = self.generate_pddl_domain()
        pddl_problems = self.generate_pddl_problems(start_events, predicates)

        output_folder = os.path.join(os.getcwd(), f'output/{self.diagram.name}')
        os.makedirs(output_folder, exist_ok = True)

        domain_file_path = os.path.join(output_folder, f'domain.pddl')
        with open(domain_file_path, 'w') as file:
            file.write(pddl_domain)

        count = 0
        for pddl_problem in pddl_problems:
            problem_file_path = os.path.join(output_folder, f'p{count:02d}.pddl')

            with open(problem_file_path, 'w') as file:
                file.write(pddl_problem)
            count += 1

    def generate_pddl_domain(self) -> tuple[str, set, list[bpmn_elements.Event]]:
        elements = self.diagram.get_elements()
        elements_by_id = {element.element_id: element for element in elements}
        used_action_names = {}
        outgoing = {}
        incoming = {}
        predicates = set()

        def get_outgoing(element_id: str) -> list: # finish type hinting
            return outgoing.get(element_id, [])
    
        def get_incoming(element_id: str) -> list:
            return incoming.get(element_id, [])
    
        for msg_flow in self.diagram.msg_flows:
            source = elements_by_id[msg_flow.startRef]
            target = elements_by_id[msg_flow.endRef]

            if self.is_valid_message_flow(source, target):
                seq_flow = self.diagram.add_sequence_flow(
                    label = 'Synthetic Sequence Flow',
                    element_id = msg_flow.element_id + '_from_msg_flow',
                    startRef = msg_flow.startRef,
                    endRef = msg_flow.endRef
                )

                elements_by_id[seq_flow.element_id] = seq_flow

        for flow in self.diagram.seq_flows:
            src = flow.startRef
            trgt = flow.endRef

            outgoing.setdefault(src, []).append(trgt)
            incoming.setdefault(trgt, []).append(src)

        parallel_converging_gateways = {}
        for gateway in self.diagram.gateways:
            incoming_len = len(get_incoming(gateway.element_id))

            if gateway.type == 'parallelGateway' and incoming_len > 1:
                parallel_converging_gateways[gateway.element_id] = [0, incoming_len]

        domain = f'(define (domain {self.diagram.name})\n\n'
        domain += '\t(:requirements\n\t\t:strips\n\t\t:typing\n\t\t:conditional-effects\n\t\t:negative-preconditions\n\t)\n'
        domain += '\t(:types\n\t\ttask event gateway\n\t)\n\n'

        domain += '\t(:predicates\n'
        for element in self.diagram.events + self.diagram.tasks + self.diagram.gateways:

            if element.type == 'exclusiveGateway':
                for seq_flow in self.diagram.seq_flows:
                    if seq_flow.startRef == element.element_id:
                        predicate = seq_flow.endRef
          
            else:
                predicate = element.element_id

            if predicate not in predicates:
                domain += f'\t\t({predicate})\n'
                predicates.add(predicate)     

            if element.type == 'inclusiveGateway':
                n_outgoing = len(get_outgoing(element.element_id))
                n_incoming = len(get_incoming(element.element_id))

                if n_incoming == 1 and n_outgoing > 1:
                    for i in range(n_outgoing + 1):
                        counter_predicate = f'inclusive_counter_{element.element_id}_{i}'
                        domain += f'\t\t({counter_predicate})\n'
                        predicates.add(counter_predicate)

                    inc_pred = f'increase_{element.element_id}'
                    dec_pred = f'decrease_{element.element_id}'

                    domain += f'\t\t({inc_pred})\n'
                    domain += f'\t\t({dec_pred})\n'
                    domain += f'\t\t(at_least_one_branch_{element.element_id})\n'

                    predicates.add(inc_pred)
                    predicates.add(dec_pred)

                    for target in get_outgoing(element.element_id):
                        branch_id = f'{element.element_id}_{target}'
                        branch_pred = f'branch_started_{branch_id}'

                        domain += f'\t\t({branch_pred})\n'
                        predicates.add(branch_pred)

        for element_id in parallel_converging_gateways.keys():
            incoming_count = parallel_converging_gateways[element_id][1]

            for i in range(incoming_count):
                predicate = f'({element_id}_precondition_{i})'

                domain += f'\t\t{predicate}\n'
                predicates.add(predicate[1 : -1])

        domain += '\t\t(finished)\n'
        domain += '\t\t(begun)\n'
        domain += '\t)\n\n'

        start_events = [event for event in self.diagram.events if event.type == 'startEvent']

        if len(start_events) == 1:
            event = start_events[0]

            domain += f'\t(:action start_{self.clean_label(event.label)}\n'
            domain += f'\t\t:parameters ()\n'
            domain += f'\t\t:precondition (and (not (begun)) (not ({event.element_id})))\n'
            domain += f'\t\t:effect (and (begun) ({event.element_id}))\n'
            domain += '\t)\n\n'

        elif len(start_events) > 1:
            start_preds = [self.clean_label(event.element_id) for event in start_events]

            domain += f'\t(:action start_process\n'
            domain += '\t\t:parameters ()\n'
            domain += f"\t\t:precondition (and (not (begun)) {' '.join(f'(not ({p}))' for p in start_preds)})\n"
            domain += f"\t\t:effect (and (begun)) {' '.join(f'({p})' for p in start_preds)}\n"
            domain += '\t)\n\n'

        converge_to_diverge = self.map_inclusive_gateway_pairs(start_events, get_outgoing, get_incoming, elements_by_id)
        generated = set()

        for gateway in self.diagram.gateways:
            gateway_id = gateway.element_id
            num_branches = len(get_outgoing(gateway_id))

            if gateway.type == 'inclusiveGateway' and len(get_incoming(gateway_id)) == 1 and num_branches > 1:
                num_branches = len(get_outgoing(gateway_id))
                counter_actions = self.generate_inclusive_counter_actions(gateway_id, num_branches)

                domain += counter_actions + '\n'
                domain += f'\t(:action inclusive_diverge_{gateway_id}\n'
                domain += f'\t\t:parameters ()\n'
                domain += f'\t\t:precondition (and ({gateway_id}))\n'
                domain += f'\t\t:effect (and\n'

                for target_id in outgoing[gateway_id]:
                    domain += f'\t\t\t(oneof\n'
                    domain += f'\t\t\t\t(and ({target_id}) (increase_{gateway_id}) (at_least_one_branch_{gateway_id}) (not ({gateway_id})))\n'
                    domain += f'\t\t\t)\n'

                domain += f'\t\t)\n'
                domain += f'\t)\n\n'

            if gateway.type == 'inclusiveGateway' and len(get_incoming(gateway_id)) > 1:
                nexts = outgoing.get(gateway_id)

                if len(nexts) == 1:
                    next_id = nexts[0]
                    diverge_id = converge_to_diverge.get(gateway_id, gateway_id)
                    predicate = self.get_parallel_gateway_precondition(gateway_id, parallel_converging_gateways, get_outgoing)

                    domain += f'\t(:action inclusive_converge_{gateway_id}\n'
                    domain += f'\t\t:parameters ()\n'
                    domain += f'\t\t:precondition (and ({gateway_id}) (at_least_one_branch_{diverge_id}) (inclusive_counter_{diverge_id}_0))\n'
                    domain += f'\t\t:effect (and ({next_id}) (not ({gateway_id})) (not (at_least_one_branch_{diverge_id})){predicate})\n'
                    domain += f'\t)\n\n'

            if not gateway.type == 'inclusiveGateway':
                targets = get_outgoing(gateway.element_id)
                precondition = f'({gateway.element_id})'

                prefix_mapping = {
                    'exclusiveGateway' : 'exclusive',
                    'parallelGateway' : 'parallel',
                    'eventBasedGateway' : 'event'
                }
                
                action_name = f'{prefix_mapping[gateway.type]}_{gateway.element_id}'

                if gateway.type == 'parallelGateway':
                    predicate = self.get_parallel_gateway_precondition(gateway.element_id, parallel_converging_gateways, get_outgoing)
                    preconds = [f'({gateway.element_id})']

                    if gateway.element_id in parallel_converging_gateways:
                        incoming_count = parallel_converging_gateways[gateway.element_id][1]

                        for i in range(incoming_count):
                            preconds.append(f'({gateway.element_id}_precondition_{i})')

                    effects = [f'({target})' for target in targets]

                    domain += f'\t(:action {action_name}\n'
                    domain += f'\t\t:parameters ()\n'
                    domain += f"\t\t:precondition (and {' '.join(preconds)})\n"
                    domain += f"\t\t:effect (and {' '.join(effects)} (not ({element.element_id})){predicate})\n"
                    domain += f'\t)\n\n'

                    generated.add(gateway.element_id)
                    continue

                elif gateway.type == 'exclusiveGateway' or gateway.type == 'eventBasedGateway':
                    oneof_effects = []

                    for target in targets:
                        effect_predicates =[f'({target})']

                        if element.type == 'eventBasedGateway':
                            next_flows = [flow for flow in self.diagram.seq_flows if flow.startRef == target]

                            for flow in next_flows:
                                next_elem = elements_by_id.get(flow.endRef)
                                
                                if next_elem and next_elem.is_gateway():
                                    effect_predicates.append(f'({next_elem.element_id})')
                        
                        if len(effect_predicates) == 1:
                            oneof_effects.append(effect_predicates[0])

                        else:
                            oneof_effects.append(f"(and {' '.join(effect_predicates)})")

                predicate = self.get_parallel_gateway_precondition(element.element_id, parallel_converging_gateways, get_outgoing)
                
                domain += f'\t(:action {action_name}\n'
                domain += f'\t\t:precondition (and {precondition})\n'
                domain += f'\t\t:effect (and'

                if len(oneof_effects) > 1:
                    domain += f"(oneof {' '.join(oneof_effects)})"

                elif len(oneof_effects) == 1:
                    domain += f' {oneof_effects[0]}'

                domain += f' (not {precondition}){predicate}\n'
                domain += '\t)\n\n'

                generated.add(element.element_id)
                continue

            else:
                if len(target) == 1:
                    effect = f'({targets[0]})'

                    domain += f'\t(:action {action_name}\n'
                    domain += f'\t\t:parameters ()\n'
                    domain += f'\t\t:precondition (and {precondition})\n'
                    domain += f'\t\t:effect (and {effect} (not {precondition}){predicate})\n'
                    domain += '\t)\n\n'

                elif len(targets) > 1:
                    effects = [f'{target}' for target in targets]
                    
                    domain += f'\t(:action {action_name}\n'
                    domain += f'\t\t:parameters ()\n'
                    domain += f'\t\t:precondition (and {precondition})\n'
                    domain += f"\t\t:effect (and {' '.join(effects)} (not {precondition}){predicate})\n"
                    domain += '\t)\n\n'

                generated.add(element.element_id)
                continue

        for task in self.diagram.tasks:
            incoming_ids = [
                src_id for src_id in get_incoming(task.element_id)
                if elements_by_id.get(src_id) and (self.is_valid_message_flow(elements_by_id.get(src_id), task) or elements_by_id.get(src_id).is_sequence_flow())
            ]

            outgoing_ids = [trgt_id for trgt_id in get_outgoing(task.element_id)]
            
            merged_sources = set(src_id for src_id in incoming_ids)
            effects = []
            oneof_effects = set()

            if len(outgoing_ids) == 1:
                effects = self.get_effects_with_following_gateways(outgoing_ids, get_outgoing, elements_by_id)

            elif len(outgoing_ids) > 1:
                for target_id in outgoing_ids:
                    branch_effects = [f'({target_id})']
                    target_element = elements_by_id.get(target_id)

                    if target_element and target_element.is_event():
                        for next_id in get_outgoing(target_id):
                            next_element = elements_by_id.get(next_id)

                            if next_element and next_element.is_gateway():
                                branch_effects.append(f'({next_element.element_id})')

                    effect_str = f"(and {' '.join(branch_effects)})" if len(branch_effects) > 1 else branch_effects[0]
                    oneof_effects.add(effect_str)
            
            oneof_effects = sorted(oneof_effects)
            inclusive_branch_sources = []

            for src_id in incoming_ids:
                src_elem = elements_by_id.get(src_id)

                if src_elem and src_elem.type == 'inclusiveGateway' and len(get_outgoing(src_elem.element_id)) > 1:
                    inclusive_branch_sources.append(src_elem.element_id)

            if len(merged_sources) > 1:
                for src_id in incoming_ids:
                    src_elem = elements_by_id.get(src_id)

                    if not src_elem:
                        continue

                    base_name = f'{task.element_id}_from_{src_elem.element_id}'
                    action_name = self.get_unique_action_name(base_name, used_action_names)

                    standard_preconditions = set()
                    branch_markers = set()

                    if src_elem:
                        if src_elem.type == 'exclusiveGateway':
                            standard_preconditions.add(f'({task.element_id})')

                        else:
                            standard_preconditions.add(f'({src_elem.element_id})')

                    if src_elem and src_elem.type == 'inclusiveGateway' and len(get_outgoing(src_elem.element_id)) > 1:
                        branch_marker = f'branch_started_{src_elem.element_id}_{task.element_id}'
                        branch_markers.add(branch_marker)
                    
                    predicate = self.get_parallel_gateway_precondition(task.element_id, parallel_converging_gateways, get_outgoing)
                    branch_markers = sorted(branch_markers)
                    standard_preconditions = sorted(standard_preconditions)

                    domain += f'\t(:action {action_name}\n'
                    domain += f'\t\t:parameters ()\n'
                    domain += f"\t\t:precondition (and {' '.join(standard_preconditions)})"

                    for marker in branch_markers:
                        domain += f' (not {marker})'
                    domain += ')\n'
                    
                    for marker in branch_markers:
                        domain += f' {marker}'
                    domain += f'\t\t:effect (and'

                    if effects:
                        domain += f" {' '.join(sorted(set(effects)))}{predicate}"

                    if oneof_effects:
                        unique_effects = list(dict.fromkeys(oneof_effects))

                        if len(unique_effects) == 1:
                            domain += f' {unique_effects[0]}{predicate}'

                        else:
                            domain += f" (oneof {' '.join(unique_effects)}{predicate})"

                    for pre in standard_preconditions:
                        domain += f' (not {pre})'

                    for marker in branch_markers:
                        domain += f' ({marker})'

                    for target_id in get_outgoing(task.element_id):
                        target_element = elements_by_id.get(target_id)

                        if target_element and target_element.type == 'inclusiveGateway' and len(get_incoming(target_element.element_id)) > 1:
                            diverging_id = converge_to_diverge.get(target_element.element_id)
                            if diverging_id:
                                domain += f' (decrease_{diverging_id})'

                    domain += ')\n'
                    domain += '\t)\n\n'
    
            else:
                has_control_gateway = any(
                    elements_by_id.get(src_id) and
                    elements_by_id.get(src_id).is_gateway() and
                    (elements_by_id.get(src_id).type == 'exclusiveGateway' or elements_by_id.get(src_id).type == 'parallelGateway')
                    for src_id in incoming_ids
                )

                branch_preconditions = set()
                branch_effects = set()
                predicate = self.get_parallel_gateway_precondition(task.element_id, parallel_converging_gateways, get_outgoing)

                if has_control_gateway:
                    standard_preconditions = {f'({task.element_id})'}

                else:
                    standard_preconditions = self.get_immediate_preconditions(task.element_id, start_events, get_outgoing, get_incoming, elements_by_id)

                for src_id in incoming_ids:
                    src_elem = elements_by_id.get(src_id)

                    if not src_elem:
                        continue

                    if src_elem.type == 'inclusiveGateway' and len(get_outgoing(src_elem.element_id)) > 1:
                        branch_name = f'branch_started_{src_elem.element_id}_{task.element_id}'
                        branch_preconditions.add(f'(not ({branch_name}))')
                        branch_effects.add(f'(branch_name)')

                base_name = self.clean_label(task.label) if task.label else task.element_id
                action_name = self.get_unique_action_name(base_name, used_action_names)

                inclusive_diverge_src = None
                for src_id in get_incoming(task.element_id):
                    src_elem = elements_by_id.get(src_id)

                    if src_elem and src_elem.type == 'inclusiveGateway' and len(get_outgoing(src_elem.element_id)) > 1:
                        inclusive_diverge_src = src_elem
                        break

                domain += f'\t(:action {action_name}\n'
                domain += f'\t\t:parameters ()\n'
                extra_preconditions = set()

                if inclusive_diverge_src:
                    extra_preconditions.add(f'(not (inclusive_counter_{inclusive_diverge_src.element_id}_0))')

                standard_preconditions = {
                    p for p in standard_preconditions
                    if not any(be.strip("()") in p for be in branch_effects)
                }

                all_preconditions = sorted(standard_preconditions | branch_preconditions | extra_preconditions)
                domain += f"\t\t:precondition (and {' '.join(all_preconditions)})\n"
                domain += f'\t\t:effect (and'

                if effects:
                    domain += f" {' '.join(sorted(set(effects)))}{predicate}"

                if oneof_effects:
                    unique_effects = list(dict.fromkeys(oneof_effects))

                    if len(unique_effects) == 1:
                        domain += f' {unique_effects[0]}{predicate}'
                    
                    else:
                        domain += f" (oneof {' '.join(unique_effects)}{predicate})"

                if inclusive_diverge_src:
                    for pre in standard_preconditions:
                        domain += f' (not {pre})'

                    for branch in sorted(branch_effects):
                        domain += f' {branch}'

                else:
                    for pre in standard_preconditions:
                        domain += f' (not {pre})'

                for target_id in get_outgoing(element.element_id):
                    target_element = elements_by_id.get(target_id)

                    if target_element and target_element.type == 'inclusiveGateway' and len(get_incoming(target_element.element_id)) > 1:
                        diverging_id = converge_to_diverge.get(target_element.element_id)

                        if diverging_id:
                            domain += f' (decrease_{diverging_id})'

                domain += ')\n'
                domain += '\t)\n\n'

        end_events = [event for event in self.diagram.events if event.type == 'endEvent']
        for event in end_events:
            domain += f'\t(:action goal_{self.clean_label(event.label)}\n'
            domain += f'\t\t:parameters ()\n'
            domain += f'\t\t:precondition (and ({event.element_id}))\n'
            domain += f'\t\t:effect (and (finished))\n'
            domain += '\t)\n\n'

        domain += ')'

        return domain, predicates, start_events

    def generate_pddl_problems(self, start_events: list[bpmn_elements.Event], predicates: set[str]) -> list[str]:
        problems = []
        count = 0

        predicates = set(predicates)
        initial_counters = sorted(p for p in predicates if p.startswith('inclusive_counter_') and p.endswith('_0'))

        marker_preds = {p for p in predicates if p.startswith('branch_started_') or p.startswith('at_least_one_branch_')}
        non_marker_preds = predicates - marker_preds

        gateways = {p for p in non_marker_preds if 'Gateway' in p}
        events = {p for p in non_marker_preds if 'Event' in p}
        tasks = {p for p in non_marker_preds if 'Activity' in p or 'Task' in p}

        events -= gateways
        tasks -= (gateways | events)

        objects = ""
        if tasks:
            objects += f"\t\t{' '.join(sorted(tasks))} - task\n"
        
        if events:
            objects += f"\t\t{' '.join(sorted(events))} - event\n"

        if gateways:
            objects += f"\t\t{' '.join(sorted(gateways))} - gateway\n"

        problem = f'(define (problem p0)\n'
        problem += f'\t(:domain {self.diagram.name})\n\n'

        problem += f'\t(:objects\n\t\t{objects.strip()}\n'
        problem += '\t)\n\n'

        problem += f"\t(:init {' '.join(f'({counter})' for counter in initial_counters)})\n\n"

        problem += '\t(:goal (and (finished)))\n\n'

        problem += ')'
        problems.append(problem)
        count += 1

        for start_event in start_events:
            initial_states = [f'({start_event.element_id})'] + [f'({counter})' for counter in initial_counters]

            problem = f'(define (problem p{count:02d})\n'
            problem += f'\t(:domain {self.diagram.name})\n\n'

            problem += f'\t(:objects\n\t\t{objects.strip()}\n'
            problem += '\t)\n\n'

            problem += f"\t(:init {' '.join(initial_states)})\n\n"

            problem += '\t(:goal (and (finished)))\n\n'

            problem += ')'
            problems.append(problem)
            count += 1

        return problems