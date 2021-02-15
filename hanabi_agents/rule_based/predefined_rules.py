from .ruleset import Ruleset
import random

flawed_rules = [
    Ruleset.play_safe_card,
    Ruleset.play_probably_safe_factory(0.25, True),
    Ruleset.tell_randomly,
    Ruleset.osawa_discard,
    Ruleset.discard_oldest_first,
    Ruleset.discard_randomly
]

iggi_rules = [
    Ruleset.play_if_certain,
    Ruleset.play_safe_card,
    Ruleset.tell_playable_card_outer,
    Ruleset.osawa_discard,
    Ruleset.discard_oldest_first,
    Ruleset.legal_random
]

outer_rules = [
    Ruleset.play_safe_card,
    Ruleset.osawa_discard,
    Ruleset.tell_playable_card_outer,
    #Ruleset.tell_unknown,
    Ruleset.discard_randomly
]

piers_rules = [
    Ruleset.hail_mary,
    #Ruleset.play_safe_card,
    Ruleset.play_probably_safe_factory(0.9999, False),
    Ruleset.play_probably_safe_factory(0.8, True),
    Ruleset.tell_anyone_useful_card,
    Ruleset.tell_dispensable_factory(3),
    Ruleset.osawa_discard,
    Ruleset.discard_oldest_first,
    Ruleset.tell_randomly,
    Ruleset.discard_randomly
]

all_rules = [
    Ruleset.discard_oldest_first,
    Ruleset.osawa_discard,
    
    #todo:buggy
    #Ruleset.tell_unknown,
    
    Ruleset.tell_randomly,
    #Ruleset.play_safe_card,
    #Ruleset.play_if_certain,
    Ruleset.tell_playable_card_outer,
    Ruleset.tell_dispensable_factory(3),
    Ruleset.tell_anyone_useful_card,
    
    #todo: test
    Ruleset.tell_anyone_useless_card,
    
    #todo:
    #Ruleset.tell_most_information,
    #Ruleset.tell_playable_card,
    
    #Ruleset.legal_random,
    #Ruleset.discard_randomly,
    
    #needs parameters:
    Ruleset.play_probably_safe_factory(0.6, True),
    Ruleset.play_probably_safe_factory(0.7, True),
    #Ruleset.discard_probably_useless_factory(0.75),

    Ruleset.hail_mary

]


big_ruleset = [
    Ruleset.play_probably_safe_factory(0.1, True),
    Ruleset.play_probably_safe_factory(0.2, True),
    Ruleset.play_probably_safe_factory(0.3, True),
    Ruleset.play_probably_safe_factory(0.4, True),
    Ruleset.play_probably_safe_factory(0.5, True),
    Ruleset.play_probably_safe_factory(0.6, True),
    Ruleset.play_probably_safe_factory(0.7, True),
    Ruleset.play_probably_safe_factory(0.8, True),
    Ruleset.play_probably_safe_factory(0.9, True),
    Ruleset.play_probably_safe_factory(0.99, True),

    Ruleset.play_probably_safe_factory(0.1, False),
    Ruleset.play_probably_safe_factory(0.2, False),
    Ruleset.play_probably_safe_factory(0.3, False),
    Ruleset.play_probably_safe_factory(0.4, False),
    Ruleset.play_probably_safe_factory(0.5, False),
    Ruleset.play_probably_safe_factory(0.6, False),
    Ruleset.play_probably_safe_factory(0.7, False),
    Ruleset.play_probably_safe_factory(0.8, False),
    Ruleset.play_probably_safe_factory(0.9, False),
    Ruleset.play_probably_safe_factory(0.99, False),

    Ruleset.discard_probably_useless_factory(0.1),
    Ruleset.discard_probably_useless_factory(0.2),
    Ruleset.discard_probably_useless_factory(0.3),
    Ruleset.discard_probably_useless_factory(0.4),
    Ruleset.discard_probably_useless_factory(0.5),
    Ruleset.discard_probably_useless_factory(0.6),
    Ruleset.discard_probably_useless_factory(0.7),
    Ruleset.discard_probably_useless_factory(0.8),
    Ruleset.discard_probably_useless_factory(0.9),
    Ruleset.discard_probably_useless_factory(0.99),

    Ruleset.tell_dispensable_factory(0),
    Ruleset.tell_dispensable_factory(1),
    Ruleset.tell_dispensable_factory(2),
    Ruleset.tell_dispensable_factory(3),
    Ruleset.tell_dispensable_factory(4),
    Ruleset.tell_dispensable_factory(5),
    Ruleset.tell_dispensable_factory(6),
    Ruleset.tell_dispensable_factory(7),
    Ruleset.tell_dispensable_factory(8),

    Ruleset.hail_mary,

    Ruleset.tell_playable_card_outer,
    Ruleset.tell_randomly,
    Ruleset.tell_anyone_useful_card,
    Ruleset.tell_anyone_useless_card,
    Ruleset.tell_most_information,
    
    Ruleset.discard_randomly,
    Ruleset.osawa_discard,
    Ruleset.discard_oldest_first
]


small_rules = [
    Ruleset.play_probably_safe_factory(0.9999, False),
    Ruleset.tell_playable_card_outer,
    Ruleset.tell_dispensable_factory(3),
    Ruleset.tell_randomly,
    Ruleset.osawa_discard,
    Ruleset.discard_oldest_first
]

test_rules = [    
    Ruleset.tell_most_information,
    Ruleset.play_probably_safe_factory(0.99,False),
    #Ruleset.tell_unknown,    
    #todo: test
    #Ruleset.tell_anyone_useless_card,
    #todo:
    #Ruleset.tell_most_information,
    Ruleset.tell_playable_card,    
    Ruleset.discard_probably_useless_factory(0.75),
    Ruleset.tell_randomly,
    Ruleset.discard_oldest_first,
    Ruleset.legal_random
]




def random_rules(num_rules = 10, used_ruleset = big_ruleset):
    rules = random.sample(used_ruleset, num_rules)
    #rules.append(Ruleset.legal_random) 
    return rules
