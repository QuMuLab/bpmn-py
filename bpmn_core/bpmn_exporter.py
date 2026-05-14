from bpmn_core import bpmn_diagram, bpmn_elements
import os
from re import sub

# TODO: 
# self.outgoing, incoming, elements, elements_by_id 
# standiarized elem_vs vs element.element_id
# use .type instead of element.element_id.startswith("Type")
# sanatize required?

class BPMNExporter:

    def __init__(self, diagram: bpmn_diagram.BPMNDiagram):
        self.diagram = diagram

    def clean_label(self, label: str) -> str:
        return sub(r'[^a-zA-Z0-9_]', '_', label)
    
    def is_valid_message_flow(source, target):
        return (isinstance(source, bpmn_elements.Task) and isinstance(target, bpmn_elements.Event)) or (isinstance(source, bpmn_elements.Event) and isinstance(target, bpmn_elements.Task))
    
    def get_immediate_preconditions(self, elem_id, incoming, outgoing, start_events, override_src = None):
        elements = self.diagram.get_elements()
        elements_by_id = {element.element_id: element for element in elements}
    
        preconditions = set()
        sources = [override_src] if override_src else incoming.get(elem_id, [])

        for src_id in sources:
            src_elem = elements_by_id.get(src_id)
            if not src_elem:
                continue

            if src_elem.element_id.startswith('ExclusiveGateway'):
                preconditions.add(f'{elem_id}')

            elif src_elem.element_id.startswith('InclusiveGateway') and len(outgoing.get(src_id, [])) > 1:
                branch_pred = f'branch_started_{src_id}_{elem_id}'

                preconditions.add(f'({branch_pred})')
                preconditions.add(f'({elem_id})')

            elif isinstance(src_elem, bpmn_elements.Event) or isinstance(src_elem, bpmn_elements.Gateway):
                preconditions.add(f'({src_id})')

            else:
                preconditions.add(f'({elem_id})')

        if not preconditions and len(start_events) == 1:
            preconditions.add(f'({start_events[0].element_id})')

        return preconditions
    
    def get_unique_action_name(self, base):
        count = self.used_action_names.get(base, 0)

        if count == 0:
            self.used_action_names[base] = 1
            return base
        
        else:
            self.used_action_names[base] += 1
            return f'{base}_{self.used_action_names[base]}'
        
    def get_effects_with_following_gateways(self, target_ids, outgoing):
        elements = self.diagram.get_elements()
        elements_by_id = {element.element_id: element for element in elements}
        effects = []

        for target_id in target_ids:
            branch_effects = {f'({target_id})'}
            target_elem = elements_by_id.get(target_id)

            if target_elem and isinstance(target_elem, bpmn_elements.Event):
                for next_id in outgoing.get(target_id, []):
                    next_elem = elements_by_id.get(next_id)

                    if next_elem and isinstance(next_elem, bpmn_elements.Gateway):
                        branch_effects.add(f'({next_elem.element_id})')

            if len(branch_effects) == 1:
                effects.append(next(iter(branch_effects)))

            else:
                effects.append(f'(and {' '.join(branch_effects)})')

        return effects

    def get_parallel_gateway_precondition(self, elem_id, outgoing, parallel_converging_gatways):
        for target_id in outgoing.get(elem_id, []):
            if target_id in parallel_converging_gatways:
                counter, incoming_count = parallel_converging_gatways[target_id]

                if counter >= incoming_count:
                    return ""
                
                predicate = f'\t{target_id}_precondition_{counter}'
                parallel_converging_gatways[target_id][0] += 1

                return predicate
            
        return ""
    
    def map_inclusive_gateway_pairs(self, incoming, outgoing, start_events):
        elements = self.diagram.get_elements()
        elements_by_id = {element.element_id: element for element in elements}
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

                if cur_id.startswith('InclusiveGateway'):
                    n_incoming = len(incoming.get(cur_id, []))
                    n_outgoing = len(outgoing.get(cur_id, []))

                    if n_incoming == 1 and n_outgoing > 1:
                        stack.append(cur_id)

                    elif n_incoming > 1 and n_outgoing == 1:
                        if stack:
                            diverging_id = stack.pop()
                            converging_id = cur_id

                            result[diverging_id] = converging_id
                            result[converging_id] = diverging_id

                for target in outgoing.get(cur_id, []):
                    if target not in visited:
                        queue.append(target)

        return result
    
    def generate_inclusive_counter_actions(self, elem_id, n):
        inc_pred = f'increase_{elem_id}'
        dec_pred = f'decrease_{elem_id}'
        lines = []

        lines.append(f'\t(:action inclusive_increase_{elem_id}')
        lines.append(f'\t\t:precondition (and ({inc_pred}))')
        lines.append('\t\t:effect (and')
        lines.append(f'\t\t\t(not ({inc_pred}))')

        for i in reversed(range(n)):
            lines.append(f'\t\t\t(when (inclusive_counter_{elem_id}_{i}) (and (not (inclusive_counter_{elem_id}_{i})) (inclusive_counter_{elem_id}_{i + 1})))')
        
        lines.append('\t\t)')
        lines.append('\t)\n')

        lines.append(f'\t(:action inclusive_decrease_{elem_id}')
        lines.append(f'\t\t:precondition (and ({dec_pred}))')
        lines.append(f'\t\t:effect (and')
        lines.append(f'\t\t\t(not ({dec_pred}))')

        for i in range (1, n + 1):
            lines.append(f'\t\t\t(when (inclusive_counter_{elem_id}_{i}) (and (not (inclusive_counter_{elem_id}_{i})) (inclusive_counter_{elem_id}_{i - 1})))')

        lines.append('\t\t)')
        lines.append('\t)\n')

        return '\n'.join(lines)
    
    def create_pddl(self):
        pddl_domain, predicates, start_events = self.generate_pddl_domain()
        pddl_problems = self.generate_pddl_problem(start_events, predicates)

        output_folder = os.path.join(os.getcwd(), f'output\\{self.diagram.name}')
        os.makedirs(output_folder, exist_ok = True)

        domain_file_path = os.path.join(output_folder, f'{self.diagram.name}_domain.pddl')
        with open(domain_file_path, 'w') as file:
            file.write(pddl_domain)

        for pddl_problem in pddl_problems:
            count = 0
            
            problem_file_path = os.path.join(output_folder, f'p{count:01d}.pddl')
            with open(problem_file_path, 'w') as file:
                file.write(pddl_problem)

    def generate_pddl_domain(self):
        elements = self.diagram.get_elements()
        elements_by_id = {element.element_id for element in elements}
        outgoing = {}
        incoming = {}
        predicates = set()
        self.unique_action_names = {}
    
        for msg_flow in self.diagram.msg_flows:
            source = elements_by_id[msg_flow.startRef]
            target = elements_by_id[msg_flow.endRef]

            if self.is_valid_message_flow(source, target):
                self.diagram.add_sequence_flow(
                    label = 'Synthetic Sequence Flow',
                    element_id = msg_flow.element_id + '_from_msg_flow',
                    startRef = msg_flow.startRef,
                    endRef = msg_flow.endRef
                )

        for flow in self.diagram.seq_flows:
            src = flow.startRef
            trgt = flow.endRef

            outgoing.setdefault(src, []).append(trgt)
            incoming.setdefault(trgt, []).append(src)

        parallel_converging_gateways = {}
        for element in elements:
            elem_id = element.element_id
            incoming_len = len(incoming.get(elem_id, []))

            if element.element_id.startswith('ParallelGateway') and incoming_len > 1:
                parallel_converging_gateways[elem_id] = [0, incoming_len]

        domain = f'(define (domain {self.diagram.name})\n'
        domain += '\t(:requirements :strips :typing)\n'
        domain += '\t(:types task event gateway)\n\n'

        domain += '\t(:predicates\n'
        for element in self.diagram.events + self.diagram.tasks + self.diagram.gateways:

            if element.element_id.startswith('ExclusiveGateway'):
                for seq_flow in self.diagram.seq_flows:
                    if seq_flow.startRef == element.element_id:
                        predicate = seq_flow.endRef
          
            else:
                predicate = element.element_id

            if predicate not in predicates:
                domain += f'\t\t({predicate})\n'
                predicates.add(predicate)     

            if element.element_id.startswith('InclusiveGateway'):
                n_outgoing = len(outgoing.get(element.element_id, []))
                n_incoming = len(incoming.get(element.element_id, []))

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

                    for target in outgoing.get(element.element_id, []):
                        branch_id = f'{element.element_id}_{target}'
                        branch_pred = f'branch_started_{branch_id}'

                        domain += f'\t\t({branch_pred})\n'
                        predicates.add(branch_pred)

        for elem_id in parallel_converging_gateways.keys():
            incoming_count = parallel_converging_gateways[elem_id][1]

            for i in range(incoming_count):
                predicate = f'({elem_id}_precondition_{i})'

                domain += f'\t\t{predicate}\n'
                predicates.add(predicate[1 : -1])

        domain += '\t\t(finished)\n'
        domain += '\t\t(begun)\n'
        domain += '\t)\n\n'

        start_events = [event for event in self.diagram.events if event.type == 'startEvent']

        if len(start_events) == 1:
            event = start_events[0]

            domain += f'\t(:action start_{self.clean_label(event.label)}\n'
            domain += f'\t\t:precondition (and (not (begun)) (not ({event.element_id})))\n'
            domain += f'\t\t:effect (and (begun) ({event.element_id}))\n'
            domain += '\t)\n\n'

        elif len(start_events) > 1:
            start_preds = [self.clean_label(event.element_id) for event in start_events]

            domain += f'\t(:action start_process\n'
            domain += f'\t\t:precondition (and (not (begun)) {' '.join(f'(not ({p}))' for p in start_preds)})\n'
            domain += f'\t\t:effect (and (begun)) {' '.join(f'({p})' for p in start_preds)}\n'
            domain += '\t)\n\n'

        converge_to_diverge = self.map_inclusive_gateway_pairs(
            incoming,
            outgoing,
            start_events
        )
        generated = set()

        for element in self.diagram.gateways:
            elem_id = element.element_id
            num_branches = len(outgoing.get(elem_id, []))

            if element.element_id.startswith('InclusiveGateway') and len(incoming.get(elem_id, [])) == 1 and num_branches > 1:
                num_branches = len(outgoing.get(elem_id, []))
                counter_actions = self.generate_inclusive_counter_actions(elem_id, num_branches)

                domain += counter_actions + '\n'
                domain += f'\t(:action inclusive_diverge_{elem_id}\n'
                domain += f'\t\t:precondition (and ({elem_id}))\n'
                domain += f'\t\t:effect (and\n'

                for target_id in outgoing[elem_id]:
                    domain += f'\t\t\t(oneof\n'
                    domain += f'\t\t\t\t(and ({target_id}) (increase_{elem_id}) (at_least_one_branch_{elem_id}) (not ({elem_id})))\n'
                    domain += f'\t\t\t)\n'

                domain += f'\t\t)\n'
                domain += f'\t)\n\n'

            if element.element_id.startswith('InclusiveGateway') and len(incoming.get(elem_id, [])) > 1:
                nexts = outgoing.get(elem_id)

                if len(nexts) == 1:
                    next_id = nexts[0]
                    diverge_id = converge_to_diverge.get(elem_id, elem_id)
                    predicate = self.get_parallel_gateway_precondition(elem_id, outgoing, parallel_converging_gateways)

                    domain += f'\t(:action inclusive_converge_{elem_id}\n'
                    domain += f'\t\t:precondition (and ({elem_id}) (at_least_one_branch_{diverge_id}) (inclusive_counter_{diverge_id}_0))\n'
                    domain += f'\t\t:effect (and ({next_id}) (not ({elem_id})) (not (at_least_one_branch_{diverge_id})) ({predicate}))\n'
                    domain += f'\t)\n\n'

            if not element.type == 'inclusiveGateway':
                targets = outgoing.get(element.element_id, [])
                precondition = f'({element.element_id})'

                prefix_mapping = {
                    'exclusiveGateway' : 'exclusive',
                    'parallelGateway' : 'parallel',
                    'eventBasedGateway' : 'event'
                }
                
                action_name = f'{prefix_mapping[element.type]}_{element.element_id}'

                if element.type == 'parallelGateway':
                    pred = self.get_parallel_gateway_precondition(element.element_id, outgoing, parallel_converging_gateways)
                    preconds = [f'({element.element_id})']

                    if element.element_id in parallel_converging_gateways:
                        incoming_count = parallel_converging_gateways[element.element_id][1]

                        for i in range(incoming_count):
                            preconds.append(f'({element.element_id}_precondition_{i})')

                    effects = [f'({target})' for target in targets]

                    domain += f'\t(:action {action_name}\n'
                    domain += f'\t\t:precondition (and {' '.join(preconds)})\n'
                    domain += f'\t\t:effect (and {' '.join(effects)} (not ({element.element_id})) ({pred}))\n'
                    domain += f'\t)\n\n'

                    generated.add(element.element_id)
                    continue

                elif element.type == 'exclusiveGateway' or element.type == 'eventBasedGateway':
                    oneof_effects = []

                    for target in targets:
                        effect_predicates =[f'({target})']

                        if element.type == 'eventBasedGateway':
                            next_flows = [flow for flow in self.diagram.seq_flows if flow.startRef == target]

                            for flow in next_flows:
                                next_elem = elements_by_id.get(flow.endRef)
                                
                                if next_elem and isinstance(next_elem, bpmn_elements.Gateway):
                                    effect_predicates.append(f'({next_elem.element_id})')
                        
                        if len(effect_predicates) == 1:
                            oneof_effects.append(effect_predicates[0])

                        else:
                            oneof_effects.append(f'(and {' '.join(effect_predicates)})')

                pred = self.get_parallel_gateway_precondition(element.element_id, outgoing, parallel_converging_gateways)
                
                domain += f'\t(action {action_name}\n'
                domain += f'\t\t:precondition (and {precondition})\n'
                domain += f'\t\t:effect (and'

                if len(oneof_effects) > 1:
                    domain += f'(oneof {' '.join(oneof_effects)})'

                elif len(oneof_effects) == 1:
                    domain += f' {oneof_effects[0]}'

                domain += f' (not {precondition}){pred}\n'
                domain += '\t)\n\n'

                generated.add(element.element_id)
                continue

            else:
                if len(target) == 1:
                    effect = f'({targets[0]})'

                    domain += f'\t(:action {action_name}\n'
                    domain += f'\t\t:precondition (and {precondition})\n'
                    domain += f'\t\t:effect (and {effect} (not {precondition}) ({pred}))\n'
                    domain += '\t)\n\n'

                elif len(targets) > 1:
                    effects = [f'{target}' for target in targets]
                    
                    domain += f'\t(:action {action_name}\n'
                    domain += f'\t\t:precondition (and {precondition})\n'
                    domain += f'\t\t:effect (and {' '.join(effects)} (not {precondition}) ({pred}))\n'
                    domain += '\t)\n\n'

                generated.add(element.element_id)
                continue

        for task in self.diagram.tasks:
            domain += f'\t(:action {self.clean_label(task.label)}\n'
            domain += f'\t\t:precondition ()\n'
            domain += f'\t\t:effect ()\n'
            domain += '\t)\n\n'

        end_events = [event for event in self.diagram.events if event.type == 'endEvent']
        for event in end_events:
            domain += f'\t(:action goal_{self.clean_label(event.label)}\n'
            domain += f'\t\t:precondition (and ({event.element_id}))\n'
            domain += f'\t\t:effect (and (finished))\n'
            domain += '\t)\n\n'

        domain += ')'
        return domain, predicates, start_events

    def generate_pddl_problem(self, start_events, predicates):
        problems = []
        count = 0

        for _ in start_events:
            problem = f'(define (problem p{count:01d})\n'
            problem += f'\t(:domain {self.diagram.name})\n\n'

            problem += '\t(:objects\n'
            problem += '\t)\n\n'

            problem += '\t(:init )\n\n'

            problem += '\t(:goal (and (finished)))\n\n'

            problem += ')'
            problems.append(problem)
            count += 1

        return problems
    
    def create_bpmn_xml(self):
        pass