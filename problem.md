# Problem
While blackjack includes a lot of luck, there is a bit of practice required to understand
when to make the proper moves. Practicing with no stakes is a good way to build your
knowledge of the game, and of course to pass the time. Casinos are dangerous and a great
way to ruin your life with a real addiction. Apps either cost money or are packed with
ads that bog down the experience.

# Initial requirements
- R1: The player starts with 2000 fake chips.
- R2: Before each hand, the player chooses how many chips to bet. The minimum bet is 100
  and the maximum is all of the player's chips.
- R3: Cards are dealt from one deck, which is reshuffled only after every card has been
  dealt. If the deck runs out during a hand, it is reshuffled and dealing continues.
- R4: The player can hit or stand.
- R5: The player can double down on any first two cards, including after a split.
- R6: The player can split when their first two cards are a pair, once per hand.
  Split aces get only one more card each.
- R7: The dealer stands on all 17s, including soft 17.
- R8: A blackjack (an ace and a ten-value card as the first two cards) pays 3 to 2.
- R9: The winner of each hand is decided by regular blackjack rules, and chips are paid
  out or lost.
- R10: The high score is the most chips the player has ever held. It is saved when the
  game is quit and is still there the next time the game starts. Current chips are not
  saved.
- R11: When the player has fewer chips than the minimum bet, the game is over and the
  player can start again with 2000 chips.
