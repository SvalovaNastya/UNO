from arbiter import Arbiter

if __name__ == "__main__":
    arbiter = Arbiter()
    players = arbiter.wait_players()
    arbiter.players = players
    arbiter.run_game()
