"""Simple Agent."""
import random
import numpy as np
from hanabi_learning_environment import pyhanabi_pybind as pyhanabi

global colors
colors = ['R', 'Y', 'G', 'W', 'B']
# ranks = [1,2,3,4,5]
num_in_deck_by_rank = [3,2,2,2,1] # Note: rank is zero-based


# Note: depending on the object calling, card could either be a dict eg {'color':'R','rank':0} or a HanabiCard instance with c.color and c.rank methods
def playable_card(card, fireworks, n_colors):
  #  if isinstance(card, pyhanabi.HanabiCard):
  #    card = {'color':colors[card.color],'rank':card.rank}

  """A card is playable if it can be placed on the fireworks pile."""
  if (card.color == pyhanabi.HanabiCard.ColorType.kUnknownColor
          and card().rank != pyhanabi.HanabiCard.RankType.kUnknownRank):
      for color in range(n_colors):
          if fireworks[color] == card.rank:
              continue
          else:
              return False

      return True
  #  elif card['color'] == None or card['rank'] == None:
  if (card.color == pyhanabi.HanabiCard.ColorType.kUnknownColor
          and card().rank == pyhanabi.HanabiCard.RankType.kUnknownRank):
      return False
  else:
      return card.rank == fireworks[card.color]

# card is not playable
def useless_card(card,fireworks,max_fireworks):
  if card.rank <= fireworks[card.color]:
    return True
  if card.rank >= max_fireworks[card.color]:
    return True
  return False



def get_plausible_cards(observation, player_offset, hand_index):
  card_knowledge = observation.hands[player_offset].knowledge
  hidden_card = card_knowledge[hand_index]
  plausible_cards = []
  for color_index in range(observation.parent_game.num_colors):
    for rank_index in range(observation.parent_game.num_ranks):
      if (hidden_card.color_plausible(color_index) and hidden_card.rank_plausible(rank_index)):
        plausible_card = pyhanabi.HanabiCard(
            pyhanabi.HanabiCard.ColorType(color_index),
            pyhanabi.HanabiCard.RankType(rank_index))
        plausible_cards.append(plausible_card)
  return plausible_cards


def get_visible_cards(observation, player_offset):
  visible_cards = []
  for other_player in range(1, observation.parent_game.num_players):
    if other_player != player_offset:
      their_hand = observation.hands[other_player]
      for card in their_hand.cards:
        visible_cards.append(card)
  for card in observation.discard_pile:
    visible_cards.append(card)
  for color, num_ranks in enumerate(observation.fireworks):
    for rank in range(num_ranks):
      card = pyhanabi.HanabiCard(
        pyhanabi.HanabiCard.ColorType(color),
        pyhanabi.HanabiCard.RankType(rank)
      )
      visible_cards.append(card)
  return visible_cards


#This returns an array of the naive probability of each card being playable from a playable from a certain player's perspective
#This ignores conventions, and also doesn't make any inferences based on the information the current player has on their hand

def get_card_playability(observation, player_offset=0):
  visible_cards = get_visible_cards(observation, player_offset)
  my_hand_size = len(observation.hands[player_offset])
  playability_array = np.zeros(my_hand_size)
  for hand_index in range(my_hand_size):
    total_possibilities = 0
    playable_possibilities = 0
    plausible_cards = get_plausible_cards(observation, player_offset, hand_index)
    for plausible in plausible_cards:
      num_in_deck = observation.parent_game.number_card_instances(plausible)
      for visible in visible_cards:
        if visible.color == plausible.color and visible.rank == plausible.rank:
          num_in_deck -= 1
      total_possibilities += num_in_deck
      if playable_card(plausible, observation.fireworks, observation.parent_game.num_colors):
        playable_possibilities += num_in_deck
    playability_array[hand_index] = playable_possibilities/total_possibilities
    
    # for plausible in plausible_cards:
    #   num_in_deck = num_in_deck_by_rank[plausible.rank]
    #   possible_in_deck += num_in_deck

    #   for other_player in range (1,observation['num_players']):
    #     if other_player != player_offset
    #       their_hand = observation['observed_hands'][other_player]:
    #         for card in their_hand:
    #           if card['color'] == plausible.color and card['rank'] == plausible.rank:
    #             possible_in_deck -=1:
      # print(num_in_deck)
      # for player in range(1,observation['num_players']):
      #   if player!= player_offset:

  return playability_array

def get_probability_useless(observation, player_offset=0):
  visible_cards = get_visible_cards(observation,player_offset)
  my_hand_size = len(observation.hands[player_offset])
  probability_useless = np.zeros(my_hand_size)
  max_fireworks = get_max_fireworks(observation)
  for hand_index in range (my_hand_size):
    total_possibilities = 0
    useless_possibilities = 0
    plausible_cards = get_plausible_cards(observation,player_offset,hand_index)
    for plausible in plausible_cards:
      num_in_deck = num_in_deck_by_rank[plausible.rank]
      for visible in visible_cards:
        #if visible['color'] == colors[plausible.color] and visible['rank'] == plausible.rank:
        if visible.color == plausible.color and visible.rank == plausible.rank:
          num_in_deck -=1
      total_possibilities += num_in_deck
      if useless_card(plausible, observation.fireworks ,max_fireworks):
        useless_possibilities += num_in_deck
    probability_useless[hand_index] = useless_possibilities/total_possibilities
    
    # for plausible in plausible_cards:
    #   num_in_deck = num_in_deck_by_rank[plausible.rank]
    #   possible_in_deck += num_in_deck

    #   for other_player in range (1,observation['num_players']):
    #     if other_player != player_offset
    #       their_hand = observation['observed_hands'][other_player]:
    #         for card in their_hand:
    #           if card['color'] == plausible.color and card['rank'] == plausible.rank:
    #             possible_in_deck -=1:
      # print(num_in_deck)
      # for player in range(1,observation['num_players']):
      #   if player!= player_offset:d



  # print (observation['pyhanabi'].card_knowledge)
  # print(player_hints)
  return probability_useless


# Note: Fireworks goes from 0 to 5, whereas rank goes from 0 to 4
def get_max_fireworks(observation):
  discarded_cards = {}
  num_colors = observation.parent_game.num_colors
  max_fireworks = {pyhanabi.HanabiCard.ColorType(c) : 5 for c in range(num_colors)}
  for card in observation.discard_pile:
    #  color = card['color']
    #  rank = card['rank']
    #  label = str(card.color) + str(card.rank)
    if card not in discarded_cards:
      discarded_cards[card] = 1
    else:
      discarded_cards[card] += 1
  for card, number_in_discard in discarded_cards.items():
    #  color = label[0]
    #  rank = int(label[1])
    #  number_in_discard = discarded_cards[card]
    if number_in_discard >= num_in_deck_by_rank[card.rank]:
      if max_fireworks[card.color] >= card.rank:
        max_fireworks[card.color] = card.rank
  #print(type(max_fireworks))
  return max_fireworks


class Ruleset():


  @staticmethod
  def discard_oldest_first(observation):
    if observation.information_tokens < observation.parent_game.max_information_tokens:
      return pyhanabi.HanabiMove(
              pyhanabi.HanabiMove.Type.kDiscard,
              0, # card index
              0, # target offset
              pyhanabi.HanabiCard.ColorType.kUnknownColor,
              pyhanabi.HanabiCard.RankType.kUnknownRank
          )
      #  return{'action_type': 'DISCARD', 'card_index': 0}
    return None

  #Note: this is not identical to the osawa rule implemented in the Fossgalaxy framework, as there the rule only takes into account explicitly known colors and ranks
  @staticmethod
  def osawa_discard(observation):
    #print(observation.information_tokens)
    if observation.information_tokens == observation.parent_game.max_information_tokens:
      return None
    fireworks = observation.fireworks
    max_fireworks = get_max_fireworks(observation)
    #safe_to_discard = False
    for card_index, card in enumerate(observation.hands[0].knowledge):
      #  color = card['color']
      #  rank = card['rank']
      if card.color is not None:
        if fireworks[card.color] == 5:
          return pyhanabi.HanabiMove(
                  pyhanabi.HanabiMove.Type.kDiscard,
                  card_index,
                  0,
                  pyhanabi.HanabiCard.ColorType.kUnknownColor,
                  pyhanabi.HanabiCard.RankType.kUnknownRank
                )
          #  return{'action_type': 'DISCARD','card_index':card_index}
      #  if (color is not None and rank is not None):
      if (card.color_hinted() and card.rank_hinted()):
        if (card.rank < fireworks[card.color] or card.rank >= max_fireworks[card.color]):
          return pyhanabi.HanabiMove(
                  pyhanabi.HanabiMove.Type.kDiscard,
                  card_index,
                  0,
                  pyhanabi.HanabiCard.ColorType.kUnknownColor,
                  pyhanabi.HanabiCard.RankType.kUnknownRank
                )
          #  return{'action_type': 'DISCARD','card_index':card_index}
      if card.rank_hinted():
        if card.rank < min(fireworks):
          return pyhanabi.HanabiMove(
                  pyhanabi.HanabiMove.Type.kDiscard,
                  card_index,
                  0,
                  pyhanabi.HanabiCard.ColorType.kUnknownColor,
                  pyhanabi.HanabiCard.RankType.kUnknownRank
                )
          #  return{'action_type': 'DISCARD','card_index':card_index}

    for card_index in range(len(observation.hands[0])):
      plausible_cards = get_plausible_cards(observation, 0, card_index)
      eventually_playable = False
      for card in plausible_cards:
        #  color = colors[card.color]
        #  rank = card.rank
        # if (rank>=fireworks[color] and rank<max_fireworks[color]):
        if (card.rank < max_fireworks[card.color]):
          eventually_playable = True
          break
      if not eventually_playable:
        return pyhanabi.HanabiMove(
                pyhanabi.HanabiMove.Type.kDiscard,
                card_index,
                0,
                pyhanabi.HanabiCard.ColorType.kUnknownColor,
                pyhanabi.HanabiCard.RankType.kUnknownRank
            )
        #  return{'action_type': 'DISCARD','card_index':card_index}
    return None


  # Note: this rule only looks at the next player on purpose, for compatibility with the Fossgalaxy implementation. Prioritizes color
  @staticmethod
  def tell_unknown(observation):
    PLAYER_OFFSET = 1
    if observation.information_tokens > 0:
      their_hand = observation.hands[PLAYER_OFFSET]
      #  their_knowledge = observation['card_knowledge'][PLAYER_OFFSET]
      for card_index, card in enumerate(their_hand.knowledge):
        if not card.color_hinted():
          #print("telling color")
          return pyhanabi.HanabiMove(
                pyhanabi.HanabiMove.Type.kRevealColor,
                card_index,
                PLAYER_OFFSET,
                pyhanabi.HanabiCard.ColorType(card.color),
                pyhanabi.HanabiCard.RankType.kUnknownRank
            )
          #  return{'action_type':'REVEAL_COLOR', 'color':their_hand[index]['color'], 'target_offset':PLAYER_OFFSET}
        if not card.rank_hinted():
          #print("telling rank")
          return pyhanabi.HanabiMove(
                pyhanabi.HanabiMove.Type.kRevealRank,
                card_index,
                PLAYER_OFFSET,
                pyhanabi.HanabiCard.ColorType.kUnknownColor,
                pyhanabi.HanabiCard.RankType(card.rank)
            )
          #  return{'action_type':'REVEAL_RANK', 'rank':their_hand[index]['rank'], 'target_offset':PLAYER_OFFSET}
    return None

    
  # Note: this rule only looks at the next player on purpose, for compatibility with the Fossgalaxy implementation. Prioritizes color
  @staticmethod
  def tell_randomly(observation):
    if observation.information_tokens > 0:
      PLAYER_OFFSET = 1
      their_hand = observation.hands[PLAYER_OFFSET]
      card_index = random.randint(0, len(their_hand) - 1)
      card = their_hand.cards[card_index]
      r = random.randint(0, 1)
      if (r == 0):
        return pyhanabi.HanabiMove(
                pyhanabi.HanabiMove.Type.kRevealRank,
                card_index,
                PLAYER_OFFSET,
                pyhanabi.HanabiCard.ColorType.kUnknownColor,
                pyhanabi.HanabiCard.RankType(card.rank)
            )
        #  return {
        #   'action_type': 'REVEAL_RANK',
        #   'rank': card['rank'],
        #   'target_offset': PLAYER_OFFSET
        #  }
      else:
        return pyhanabi.HanabiMove(
                pyhanabi.HanabiMove.Type.kRevealColor,
                card_index,
                PLAYER_OFFSET,
                pyhanabi.HanabiCard.ColorType(card.color),
                pyhanabi.HanabiCard.RankType.kUnknownRank
            )
        #  return {
        #   'action_type': 'REVEAL_COLOR',
        #   'color': card['color'],
        #   'target_offset': PLAYER_OFFSET
        #  }
    return None

  @staticmethod
  def play_safe_card(observation):
    PLAYER_OFFSET = 0
    fireworks = observation.fireworks
    # # for card_index, hint in enumerate(observation['card_knowledge'][0]):
    # #   if playable_card(hint, fireworks):
    # #       return {'action_type': 'PLAY', 'card_index': card_index}
    # playability_vector = get_card_playability(observation)
    # card_index = np.argmax(playability_vector)
    # if playability_vector[card_index]==1:
    #   action = {'action_type': 'PLAY', 'card_index': card_index}
    #   return action

    hand = observation.hands[0]
    for card_index, hint in enumerate(hand.knowledge):
      plausible_cards = get_plausible_cards(observation, PLAYER_OFFSET, card_index)
      definetly_playable = True
      for plausible in plausible_cards:
        if not playable_card(plausible, fireworks, observation.parent_game.num_colors):
          definetly_playable = False
          break
      if definetly_playable:
        action = pyhanabi.HanabiMove(
          pyhanabi.HanabiMove.Type.kPlay,
          card_index,
          PLAYER_OFFSET,
          hint.color,
          hint.rank
        )
        #  action = {'action_type': 'PLAY', 'card_index': card_index}
        return action
    return None

  @staticmethod
  def play_if_certain(observation):
    PLAYER_OFFSET = 0
    fireworks = observation.fireworks
    # # for card_index, hint in enumerate(observation['card_knowledge'][0]):
    # #   if playable_card(hint, fireworks):
    # #       return {'action_type': 'PLAY', 'card_index': card_index}
    # playability_vector = get_card_playability(observation)
    # card_index = np.argmax(playability_vector)
    # if playability_vector[card_index]==1:
    #   action = {'action_type': 'PLAY', 'card_index': card_index}
    #   return action

    #  for card_index, card in enumerate(observation['card_knowledge'][0]):
    for card_index, knowledge in enumerate(observation.hands[0].knowledge):
      #  color = card['color']
      #  rank = card['rank']
      if knowledge.color_hinted() and knowledge.rank_hinted():
        if  knowledge.rank == fireworks[knowledge.color]:
          return pyhanabi.HanabiMove(
            pyhanabi.HanabiMove.Type.kPlay,
            card_index,
            PLAYER_OFFSET,
            knowledge.color,
            knowledge.rank
            )
          #  return{'action_type': 'PLAY', 'card_index': card_index}
    return None

  # Prioritizes Rank
  @staticmethod
  def tell_playable_card_outer(observation):
    fireworks = observation.fireworks

    # Check if it's possible to hint a card to your colleagues.
    if observation.information_tokens > 0:
      # Check if there are any playable cards in the hands of the opponents.
      for player_offset in range(1, observation.parent_game.num_players):
        player_hand = observation.hands[player_offset]
        #  player_hints = observation['card_knowledge'][player_offset]
        # Check if the card in the hand of the opponent is playable.
        for card_index, (card, hint) in enumerate(zip(player_hand.cards, player_hand.knowledge)):
          card_playable = playable_card(card, fireworks, observation.parent_game.num_colors)
          if card_playable and not hint.rank_hinted():
            return pyhanabi.HanabiMove(
                    pyhanabi.HanabiMove.Type.kRevealRank,
                    card_index,
                    player_offset,
                    pyhanabi.HanabiCard.ColorType.kUnknownColor,
                    pyhanabi.HanabiCard.RankType(card.rank)
                )
        #  {
        #       'action_type': 'REVEAL_RANK',
        #       'rank': card['rank'],
        #       'target_offset': player_offset
        #      }
          elif card_playable and not hint.color_hinted():
            return pyhanabi.HanabiMove(
                    pyhanabi.HanabiMove.Type.kRevealColor,
                    card_index,
                    player_offset,
                    pyhanabi.HanabiCard.ColorType(card.color),
                    pyhanabi.HanabiCard.RankType.kUnknownRank
                )
            #  {
            #   'action_type': 'REVEAL_COLOR',
            #   'color': card['color'],
            #   'target_offset': player_offset
            #  }
    return None

  @staticmethod
  def tell_dispensable_factory(min_information_tokens=8):
    def tell_dispensable(observation):
      if (observation.information_tokens < min_information_tokens):
        fireworks = observation.fireworks

        # Check if it's possible to hint a card to your colleagues.
        if observation.information_tokens > 0:
          # Check if there are any playable cards in the hands of the opponents.
          for player_offset in range(1, observation.parent_game.num_players):
            player_hand = observation.hands[player_offset]
            # Check if the card in the hand of the opponent is playable.
            for card_index, (card, hint) in enumerate(zip(player_hand.cards, player_hand.knowledge)):
              #  color = card['color']
              #  rank = card['rank']
              #  known_color = hint['color']
              #  known_rank = hint['rank']
              #  if known_color is None and fireworks[color] == 5:
              if not hint.color_hinted() and fireworks[card.color] == 5:

                return pyhanabi.HanabiMove(
                        pyhanabi.HanabiMove.Type.kRevealColor,
                        card_index,
                        player_offset,
                        card.color,
                        pyhanabi.HanabiCard.RankType.kUnknownRank
                    )
                #  return {'action_type':'REVEAL_COLOR','color':color,'target_offset':player_offset}
              #  if known_rank is None and rank < min(fireworks.values()):
              if not hint.rank_hinted() and card.rank < min(fireworks):
                return pyhanabi.HanabiMove(
                        pyhanabi.HanabiMove.Type.kRevealRank,
                        card_index,
                        player_offset,
                        pyhanabi.HanabiCard.ColorType.kUnknownColor,
                        card.rank
                    )
                #  return {'action_type':'REVEAL_RANK','rank':rank,'target_offset':player_offset}
              #  if rank < fireworks[color]:
              if card.rank < fireworks[card.color]:
                #  if known_color is None and known_rank is not None:
                if not hint.color_hinted() and hint.rank_hinted():
                  return pyhanabi.HanabiMove(
                          pyhanabi.HanabiMove.Type.kRevealColor,
                          card_index,
                          player_offset,
                          card.color,
                          pyhanabi.HanabiCard.RankType.kUnknownRank
                      )
                   #  return {'action_type':'REVEAL_COLOR','color':color,'target_offset':player_offset}
                #  if known_color is not None and known_rank is None:
                if hint.color_hinted() and not hint.rank_hinted():
                  return pyhanabi.HanabiMove(
                          pyhanabi.HanabiMove.Type.kRevealRank,
                          card_index,
                          player_offset,
                          pyhanabi.HanabiCard.ColorType.kUnknownColor,
                          card.rank
                      )
                    #  return {'action_type':'REVEAL_RANK','rank':rank,'target_offset':player_offset}
      return None
    return tell_dispensable

  # As far as I can tell, this is functinally identical to Tell Playable Outer
  @staticmethod
  def tell_anyone_useful_card(observation):
    return Ruleset.tell_playable_card_outer(observation)

  @staticmethod
  def tell_anyone_useless_card(observation):
    fireworks = observation.fireworks
    if observation.information_tokens > 1:
      max_fireworks = get_max_fireworks(observation)
      for player_offset in range(1, observation.parent_game.num_players):
        player_hand = observation.hands[player_offset]
        for card_index, (card, hint) in enumerate(zip(player_hand.cards, player_hand.knowledge)):
          if useless_card(card,fireworks,max_fireworks):
            if hint.color_hinted() is None:
              return pyhanabi.HanabiMove(
                      pyhanabi.HanabiMove.Type.kRevealColor,
                      card_index,
                      player_offset,
                      card.color,
                      pyhanabi.HanabiCard.RankType.kUnknownRank
                  )              
              #return {'action_type':'REVEAL_COLOR','color':card['color'],'target_offset':player_offset}
            if hint.rank_hinted() is None:
              return pyhanabi.HanabiMove(
                      pyhanabi.HanabiMove.Type.kRevealRank,
                      card_index,
                      player_offset,
                      pyhanabi.HanabiCard.ColorType.kUnknownColor,
                      pyhanabi.HanabiCard.RankType(card.rank)
                  )
              # return {'action_type':'REVEAL_RANK','rank':card['rank'],'target_offset':player_offset}
    return None

  # Note: this follows the version of the rule that's used on VanDenBergh, which does not take into account whether or not they already know that information
  @staticmethod
  def tell_most_information(observation):
    #fireworks = observation.fireworks
    best_action = None
    if observation.information_tokens >= 1:
      #max_fireworks = get_max_fireworks(observation)
      max_affected = -1
      for player_offset in range(1, observation.parent_game.num_players):
        player_hand = observation.hands[player_offset]
        #print("cards: ", player_hand.cards)
        #print("knowledge: ", player_hand.knowledge)
        for card_index, (card, hint) in enumerate(zip(player_hand.cards, player_hand.knowledge)):
          affected_colors = 0
          affected_ranks = 0
          for other_card, other_hint in zip(player_hand.cards, player_hand.knowledge):
            if card.color == other_card.color and not other_hint.color_hinted():
              affected_colors+=1
            if card.rank  == other_card.rank and not other_hint.rank_hinted():
              affected_ranks+=1
          if affected_colors > max_affected:
            max_affected = affected_colors
            #best_action = {'action_type':'REVEAL_COLOR','color':card['color'],'target_offset':player_offset}
            best_action = pyhanabi.HanabiMove(
                      pyhanabi.HanabiMove.Type.kRevealColor,
                      card_index,
                      player_offset,
                      card.color,
                      pyhanabi.HanabiCard.RankType.kUnknownRank
                  )  
          if affected_ranks > max_affected:
            max_affected = affected_ranks
            #best_action = {'action_type':'REVEAL_RANK','rank':card['rank'],'target_offset':player_offset}
            best_action = pyhanabi.HanabiMove(
                      pyhanabi.HanabiMove.Type.kRevealRank,
                      card_index,
                      player_offset,
                      pyhanabi.HanabiCard.ColorType.kUnknownColor,
                      pyhanabi.HanabiCard.RankType(card.rank)
                  )
    #print(best_action)
    #print("")
    return best_action



  #tells rank or color at random if tell_rank is unspecified, tells rank if set to 1, color if set to 0.
  @staticmethod
  def tell_playable_card(observation, tell_rank = random.randint(0,1)):
    fireworks = observation.fireworks

    # Check if it's possible to hint a card to your colleagues.
    if observation.information_tokens > 0:
      # Check if there are any playable cards in the hands of the opponents.
      for player_offset in range(1, observation.parent_game.num_players):
        player_hand = observation.hands[player_offset]
        # Check if the card in the hand of the opponent is playable.
        for card_index, (card, hint) in enumerate(zip(player_hand.cards, player_hand.knowledge)):
          if playable_card(card, fireworks, observation.parent_game.num_colors):
            if (tell_rank and not hint.rank_hinted()):
              #print("fireworks:", fireworks)
              #print("telling: ", card)
              return pyhanabi.HanabiMove(
                      pyhanabi.HanabiMove.Type.kRevealRank,
                      card_index,
                      player_offset,
                      pyhanabi.HanabiCard.ColorType.kUnknownColor,
                      card.rank
                  )
              
              
              #{ 'action_type': 'REVEAL_RANK', 'rank': card['rank'],'target_offset': player_offset}
            elif (not hint.color_hinted()):
              #print("fireworks: ",fireworks)
              #print("telling: ", card)
              return pyhanabi.HanabiMove(
                        pyhanabi.HanabiMove.Type.kRevealColor,
                        card_index,
                        player_offset,
                        card.color,
                        pyhanabi.HanabiCard.RankType.kUnknownRank
                  ) 
              
              #{'action_type': 'REVEAL_COLOR','color': card['color'],'target_offset': player_offset}
            
            #if you wan to tell the color but already now the color you tell the rank instead
            elif(not hint.rank_hinted()):
              #print("fireworks: ", fireworks)
              #print("telling: ", card)
              return pyhanabi.HanabiMove(
                      pyhanabi.HanabiMove.Type.kRevealRank,
                      card_index,
                      player_offset,
                      pyhanabi.HanabiCard.ColorType.kUnknownColor,
                      card.rank
                  )
    return None


  @staticmethod
  def legal_random(observation):
    """Act based on an observation."""
    #if observation.cur_player_offset == 0:
    action = random.choice(observation.legal_moves)
    #print(action)
    return action
    #else:
    #  return None

  @staticmethod
  def discard_randomly(observation):
    #print("discarding")
    if observation.information_tokens < 8:
      player_offset = 0
      hand = observation.hands[player_offset]
      hand_size = len(hand)
      discard_index = random.randint(0,hand_size-1)
      return pyhanabi.HanabiMove(
              pyhanabi.HanabiMove.Type.kDiscard,
              discard_index,
              0,
              pyhanabi.HanabiCard.ColorType.kUnknownColor,
              pyhanabi.HanabiCard.RankType.kUnknownRank
            )
      #return {'action_type': 'DISCARD', 'card_index': discard_index}
    return None

  @staticmethod
  def play_probably_safe_factory(treshold = 0.95, require_extra_lives = False):
    def play_probably_safe_treshold(observation):
      playability_vector = observation.playable_percent()
      #print("old, ", get_card_playability(observation) )
      #print("new, ", playability_vector)
      card_index = np.argmax(playability_vector)
      #print(playability_vector)
      if not require_extra_lives or observation.life_tokens >1:
        if playability_vector[card_index]>=treshold:
          action = pyhanabi.HanabiMove(
            pyhanabi.HanabiMove.Type.kPlay,
            card_index,
            0,
            pyhanabi.HanabiCard.ColorType.kUnknownColor,
            pyhanabi.HanabiCard.RankType.kUnknownRank
            )

          #  action = {'action_type': 'PLAY', 'card_index': card_index}
          return action
      return None

    return play_probably_safe_treshold

  @staticmethod
  def discard_probably_useless_factory(treshold = 0.75):
    def play_probably_useless_treshold(observation):
      if observation.information_tokens < observation.parent_game.max_information_tokens: 
        #probability_useless_old = get_probability_useless(observation)
        #print("player offset: ", observation.current_player_offset)
        #print("old: ",probability_useless)
        probability_useless = observation.discardable_percent()
        #print("new: ", probability_useless2)
        #print("colors: ", colors)
        #print("max_fireworks: ", list(get_max_fireworks(observation).values()))
        #print("fireworks: ", observation.fireworks)
        #print("hand: ", observation.hands[0].knowledge)
        #print("")

        # print("probability useless" +str(probability_useless))
        card_index = np.argmax(probability_useless)
        if probability_useless[card_index]>=treshold:
          #action = {'action_type': 'DISCARD', 'card_index': card_index}
          return pyhanabi.HanabiMove(
                  pyhanabi.HanabiMove.Type.kDiscard,
                  card_index,
                  0,
                  pyhanabi.HanabiCard.ColorType.kUnknownColor,
                  pyhanabi.HanabiCard.RankType.kUnknownRank
                )          
          #return action
      return None

    return play_probably_useless_treshold

  # "Hail Mary" rule used by agent Piers
  @staticmethod
  def hail_mary(observation):
    if (observation.deck_size == 0 and observation.life_tokens > 1):
      return Ruleset.play_probably_safe_factory(0.0)(observation)
