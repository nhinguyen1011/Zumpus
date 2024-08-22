from pysat.formula import CNF
from pysat.solvers import Solver

class KnowledgeBase:
    def __init__(self):
        self.facts = set()
        self.implications = []
        self.solver = Solver(bootstrap_with=[])

    def add_fact(self, fact):
        """Add a fact to the knowledge base."""
        self.facts.add(fact)
        print(f"Fact added: {fact}")

    def remove_fact(self, fact):
        """Remove a fact from the knowledge base."""
        if fact in self.facts:
            self.facts.remove(fact)
            print(f"Fact removed: {fact}")

    def add_implication(self, premise, conclusion):
        """Add an implication (rule) to the knowledge base."""
        self.implications.append((premise, conclusion))
        print(f"Rule added: {premise} -> {conclusion}")

    def query(self, fact):
        """Query whether a fact is true based on the current knowledge."""
        # Check if the fact is explicitly known
        if fact in self.facts:
            return True
        
        # Check if the fact can be inferred using implications
        for premise, conclusion in self.implications:
            if premise in self.facts and conclusion == fact:
                return True
        
        return False

    def apply_logic(self):
        """Apply logic to derive new facts based on the implications."""
        new_facts = set()
        for premise, conclusion in self.implications:
            if premise in self.facts and conclusion not in self.facts:
                new_facts.add(conclusion)
        
        # Add all derived facts to the knowledge base
        self.facts.update(new_facts)
        return new_facts

    def add_to_cnf(self, clause):
        """Add a clause to the CNF formula and to the SAT solver."""
        cnf = CNF()
        cnf.append(clause)
        self.solver.append_formula(cnf)

    def check_sat(self, assumptions):
        """Check if the assumptions are satisfiable using the SAT solver."""
        return self.solver.solve(assumptions)

    def explain(self, fact):
        """Explain why a fact is true, if it is."""
        if fact in self.facts:
            return f"{fact} is known as a fact."
        for premise, conclusion in self.implications:
            if conclusion == fact and premise in self.facts:
                return f"{fact} is inferred from {premise}."
        return f"No explanation for {fact}."

    def update_knowledge(self, fact, is_present):
        """Update knowledge based on new information about a fact's presence."""
        if not is_present:
            # If the fact is not present, remove any implications related to it
            self.remove_fact(fact)
            # Assuming 'fact' is in the form 'Wumpus at (x,y)'
            negated_fact = f"not {fact}"
            self.add_fact(negated_fact)  # Mark the fact as not present
            self.remove_related_implications(fact)
        else:
            self.add_fact(fact)
        self.apply_logic()

    def remove_related_implications(self, fact):
        """Remove implications related to a fact."""
        self.implications = [(p, c) for p, c in self.implications if p != fact and c != fact]
        print(f"Removed implications related to {fact}")


