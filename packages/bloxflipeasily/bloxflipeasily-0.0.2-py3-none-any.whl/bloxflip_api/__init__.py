"""A bloxflip api wrapper made by https://www.youtube.com/channel/UCqYdlD1g_fUCZxzjMHNgYnw"""
import cloudscraper

scraper = cloudscraper.create_scraper()


class User:
    """The Class User for bloxflip"""

    def __init__(self, auth: str) -> None:
        self.auth = auth

#checking if auth vaild

    def is_valid(self,
                 invalid_auth_message=None,
                 valid_auth_message=None) -> None:
        """A simple script to check if the user has a valid auth"""
        r = scraper.get("https://rest-bf.blox.land/user",
                        headers={
                            "x-auth-token": self.auth
                        }).json()
        if not r["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            if r["success"] is True:
                return "User's auth is valid" if valid_auth_message is None else valid_auth_message
#grabing the user's robux

    def userRobux(self, invalid_auth_message=None) -> None:
        """Grab the user's robux/wallet in formatted form"""
        user = scraper.get("https://rest-bf.blox.land/user",
                           headers={
                               "x-auth-token": self.auth
                           }).json()
        if not user["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            wallet = user["user"]["wallet"]
            return f"{wallet:.2f}"
#returning test for owner's and those who need it

    def test(self) -> None:
        """Mainly used for testing the package."""
        return (scraper.get("https://rest-bf.blox.land/user",
                            headers={"x-auth-token": self.auth})).json()

    def userWagered(self, invalid_auth_message=None) -> None:
        """Grab the user's wagered"""
        user = scraper.get("https://rest-bf.blox.land/user",
                           headers={
                               "x-auth-token": self.auth
                           }).json()
        if not user["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            wagered = user["user"]["wager"]
            return f"{wagered:.2f}"

    def userWithdrawn(self, invalid_auth_message=None) -> None:
        """Grab the totalWithdrawn from the bloxflip api, returningg how much the user has withdrawn"""
        user = scraper.get("https://rest-bf.blox.land/user",
                           headers={
                               "x-auth-token": self.auth
                           }).json()
        if not user["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            withdrawn = user["user"]["totalWithdrawn"]
            return f"{withdrawn:.2f}"


#rank

    def userRanked(self, invalid_auth_message: str = None) -> None:
        """Get what rank the user is"""
        user = scraper.get("https://rest-bf.blox.land/user",
                           headers={
                               "x-auth-token": self.auth
                           }).json()
        if not user["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            ranked = user['user']["rank"]
            return ranked

    def userUsername(self, invalid_auth_message: str = None) -> None:
        user = scraper.get("https://rest-bf.blox.land/user",
                           headers={
                               "x-auth-token": self.auth
                           }).json()
        if not user["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            userName = user["user"]["robloxUsername"]
            return userName

    def userID(self, invalid_auth_message: str = None) -> None:
        """Get the user's user ID"""
        user = scraper.get("https://rest-bf.blox.land/user",
                           headers={
                               "x-auth-token": self.auth
                           }).json()
        if not user["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            userID = user["user"]["robloxId"]
            return userID

    def userAffliate(self,
                     invalid_auth_message: str = None,
                     no_code_message: str = None) -> None:
        user = scraper.get("https://rest-bf.blox.land/user",
                           headers={
                               "x-auth-token": self.auth
                           }).json()
        if not user["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            affliate_code = user["user"]["affiliateCode"]
            if affliate_code == None and no_code_message == None:
                return "User has no affliate code"
            else:
                affliate_code = user["user"]["affiliateCode"]
                if affliate_code == None and no_code_message != None:
                    return no_code_message
                else:
                    return affliate_code

    def userTimeZone(self, invalid_auth_message: str = None) -> None:
        user = scraper.get("https://rest-bf.blox.land/user",
                           headers={
                               "x-auth-token": self.auth
                           }).json()
        if not user["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            time_zone = user["user"]["timezoneId"]
            return time_zone

    def userAffliateMoney(self, invalid_auth_message: str = None) -> None:
        user = scraper.get("https://rest-bf.blox.land/user",
                           headers={
                               "x-auth-token": self.auth
                           }).json()
        if not user["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            return user["user"]["affiliateMoney"]

    def userAffliateCollectedMoney(self,
                                   invalid_auth_message: str = None) -> None:
        user = scraper.get("https://rest-bf.blox.land/user",
                           headers={
                               "x-auth-token": self.auth
                           }).json()
        if not user["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            return user["user"]["affiliateMoneyCollected"]

    def userUniqueDeviceID(self, invalid_auth_message=None) -> None:
        user = scraper.get("https://rest-bf.blox.land/user",
                           headers={
                               "x-auth-token": self.auth
                           }).json()
        if not user["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            return user["user"]["uniqueDeviceId"]


class Grab:

    def crash(games: int):
        if games > 35:
            return "Sorry only 35 games are allowed to be grabbed"
        else:
            history = scraper.get(
                "https://rest-bf.blox.land/games/crash").json()["history"]
            data = [crashPoint["crashPoint"] for crashPoint in history][:games]
            return data

    def roulette(games: int):
        if games > 35:
            return "Sorry only 35 games are allowed to be grabbed"
        else:
            history = scraper.get(
                "https://rest-bf.blox.land/games/roulette").json()["history"]
            data = [winningColor["winningColor"]
                    for winningColor in history][:games]
            return data

    def uncovered_locations(games: int,
                            auth: str,
                            invalid_auth_message: str = None,
                            invaild_games_message: int = None):
        try:
            user = scraper.get("https://rest-bf.blox.land/user",
                               headers={
                                   "x-auth-token": auth
                               }).json()
            if not user["success"]:
                return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
            else:
                url = 'https://rest-bf.blox.land/games/mines/history'
                headers = {"x-auth-token": auth}
                params = {"size": games, "page": 0}
                data = scraper.get(url, headers=headers,
                                   params=params).json()["data"]
                dataa = [
                    uncoveredMines["mineLocations"] for uncoveredMines in data
                ]
                return dataa
        except KeyError:
            if invaild_games_message == None:
                return "Error: The games you have entered is more than the size"
            else:
                if invaild_games_message != None:
                    return invaild_games_message

    def uncovered_mines(games: int,
                        auth: str,
                        invalid_auth_message: str = None,
                        invaild_games_message: int = None):
        try:
            user = scraper.get("https://rest-bf.blox.land/user",
                               headers={
                                   "x-auth-token": auth
                               }).json()
            if not user["success"]:
                return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
            else:
                url = 'https://rest-bf.blox.land/games/mines/history'
                headers = {"x-auth-token": auth}
                params = {"size": games, "page": 0}
                data = scraper.get(url, headers=headers,
                                   params=params).json()["data"]
                dataa = [
                    uncoveredMines["uncoveredLocations"]
                    for uncoveredMines in data
                ]
                return dataa
        except KeyError:
            if invaild_games_message == None:
                return "Error: The games you have entered is more than the size"
            else:
                if invaild_games_message != None:
                    return invaild_games_message

    def towerLevels(games: int,
                    auth: str,
                    invalid_auth_message: str = None,
                    invaild_games_message: int = None):
        try:
            user = scraper.get("https://rest-bf.blox.land/user",
                               headers={
                                   "x-auth-token": auth
                               }).json()
            if not user["success"]:
                return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
            else:
                url = 'https://rest-bf.blox.land/games/towers/history'
                headers = {"x-auth-token": auth}
                params = {"size": games, "page": 0}
                data = scraper.get(url, headers=headers,
                                   params=params).json()["data"]
                dataa = [
                    uncoveredMines["towerLevels"] for uncoveredMines in data
                ]
                return dataa
        except KeyError:
            if invaild_games_message == None:
                return "Error: The games you have entered is more than the size"
            else:
                if invaild_games_message != None:
                    return invaild_games_message


class ActiveMines:

    def __init__(self, auth: str) -> None:
        self.auth = auth

    def hasGame(self,
                no_game_message=None,
                invalid_auth_message=None,
                active_true=None) -> None:
        user = scraper.get("https://rest-bf.blox.land/user",
                           headers={
                               "x-auth-token": self.auth
                           }).json()
        if not user["success"]:
            return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
        else:
            if no_game_message == None:
                hasGame = scraper.get("https://rest-bf.blox.land/games/mines",
                                      headers={
                                          "x-auth-token": self.auth
                                      }).json()
                if hasGame["hasGame"] == False and no_game_message == None:
                    return "User has no game"
                else:
                    if hasGame["hasGame"] == False and no_game_message != None:
                        return no_game_message
                    else:
                        if active_true == None and hasGame["hasGame"] == True:
                            return "User has a game"
                        else:
                            if active_true != None and hasGame[
                                    "hasGame"] == True:
                                return hasGame

    def gameMultiplier(self,
                       invalid_auth_message=None,
                       already_has_game_message=None) -> None:
        try:
            user = scraper.get("https://rest-bf.blox.land/user",
                               headers={
                                   "x-auth-token": self.auth
                               }).json()
            if not user["success"]:
                return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
            else:
                game = scraper.get("https://rest-bf.blox.land/games/mines",
                                   headers={
                                       "x-auth-token": self.auth
                                   }).json()
                return game["multiplier"]
        except KeyError:
            if already_has_game_message == None:
                return "Sorry you don't have a game or another error is occuring"
            else:
                if already_has_game_message == None:
                    return already_has_game_message

    def gameRoundID(self,
                    invalid_auth_message=None,
                    already_has_game_message=None) -> None:
        try:
            user = scraper.get("https://rest-bf.blox.land/user",
                               headers={
                                   "x-auth-token": self.auth
                               }).json()
            if not user["success"]:
                return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
            else:
                game = scraper.get("https://rest-bf.blox.land/games/mines",
                                   headers={
                                       "x-auth-token": self.auth
                                   }).json()
                return game["game"]["uuid"]
        except KeyError:
            if already_has_game_message == None:
                return "Sorry you don't have a game or another error is occurcing"
            else:
                if already_has_game_message == None:
                    return already_has_game_message

    def gamebetAmount(self,
                      invalid_auth_message=None,
                      already_has_game_message=None) -> None:
        try:
            user = scraper.get("https://rest-bf.blox.land/user",
                               headers={
                                   "x-auth-token": self.auth
                               }).json()
            if not user["success"]:
                return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
            else:
                game = scraper.get("https://rest-bf.blox.land/games/mines",
                                   headers={
                                       "x-auth-token": self.auth
                                   }).json()
                return game["game"]["betAmount"]
        except KeyError:
            if already_has_game_message == None:
                return "Sorry you don't have a game or another error is occuring"
            else:
                if already_has_game_message == None:
                    return already_has_game_message

    def gamePayout(self,
                   invalid_auth_message=None,
                   already_has_game_message=None) -> None:
        try:
            user = scraper.get("https://rest-bf.blox.land/user",
                               headers={
                                   "x-auth-token": self.auth
                               }).json()
            if not user["success"]:
                return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
            else:
                game = scraper.get("https://rest-bf.blox.land/games/mines",
                                   headers={
                                       "x-auth-token": self.auth
                                   }).json()
                return game["game"]["payout"]
        except KeyError:
            if already_has_game_message == None:
                return "Sorry you don't have a game or another error is occuring"
            else:
                if already_has_game_message == None:
                    return already_has_game_message

    def gameClientSeed(self,
                       invalid_auth_message=None,
                       already_has_game_message=None) -> None:
        try:
            user = scraper.get("https://rest-bf.blox.land/user",
                               headers={
                                   "x-auth-token": self.auth
                               }).json()
            if not user["success"]:
                return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
            else:
                game = scraper.get("https://rest-bf.blox.land/games/mines",
                                   headers={
                                       "x-auth-token": self.auth
                                   }).json()
                return game["game"]["clientSeed"]
        except KeyError:
            if already_has_game_message == None:
                return "Sorry you don't have a game or another error is occurcing"
            else:
                if already_has_game_message == None:
                    return already_has_game_message

    def gameNonce(self,
                  invalid_auth_message=None,
                  already_has_game_message=None) -> None:
        try:
            user = scraper.get("https://rest-bf.blox.land/user",
                               headers={
                                   "x-auth-token": self.auth
                               }).json()
            if not user["success"]:
                return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
            else:
                game = scraper.get("https://rest-bf.blox.land/games/mines",
                                   headers={
                                       "x-auth-token": self.auth
                                   }).json()
                return game["game"]["nonce"]
        except KeyError:
            if already_has_game_message == None:
                return "Sorry you don't have a game or another error is occurcing"
            else:
                if already_has_game_message == None:
                    return already_has_game_message

    def gameMinesAmount(self,
                        invalid_auth_message=None,
                        already_has_game_message=None) -> None:
        try:
            user = scraper.get("https://rest-bf.blox.land/user",
                               headers={
                                   "x-auth-token": self.auth
                               }).json()
            if not user["success"]:
                return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
            else:
                game = scraper.get("https://rest-bf.blox.land/games/mines",
                                   headers={
                                       "x-auth-token": self.auth
                                   }).json()
                return game["game"]["minesAmount"]
        except KeyError:
            if already_has_game_message == None:
                return "Sorry you don't have a game or another error is occurcing"
            else:
                if already_has_game_message == None:
                    return already_has_game_message

    def gameClickedMinesLocations(self,
                                  invalid_auth_message=None,
                                  already_has_game_message=None) -> None:
        """"""
        try:
            user = scraper.get("https://rest-bf.blox.land/user",
                               headers={
                                   "x-auth-token": self.auth
                               }).json()
            if not user["success"]:
                return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
            else:
                game = scraper.get("https://rest-bf.blox.land/games/mines",
                                   headers={
                                       "x-auth-token": self.auth
                                   }).json()
                return game["game"]["badMineUncovered"]
        except KeyError:
            if already_has_game_message == None:
                return "Sorry you don't have a game or another error is occurcing"
            else:
                if already_has_game_message == None:
                    return already_has_game_message

    def gameClickedUncoveredLocations(self,
                                      invalid_auth_message=None,
                                      already_has_game_message=None) -> None:
        try:
            """get's the uncovered locations from the gam that u clicked"""
            user = scraper.get("https://rest-bf.blox.land/user",
                               headers={
                                   "x-auth-token": self.auth
                               }).json()
            if not user["success"]:
                return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
            else:
                game = scraper.get("https://rest-bf.blox.land/games/mines",
                                   headers={
                                       "x-auth-token": self.auth
                                   }).json()
                return game["game"]["uncoveredLocations"]
        except KeyError:
            if already_has_game_message == None:
                return "Sorry you don't have a game or another error is occurcing"
            else:
                if already_has_game_message == None:
                    return already_has_game_message


class uuid:
    """Grab the uuid from games"""

    def crash():
        return (scraper.get("https://rest-bf.blox.land/games/crash").json()
                ["current"]["_id"])

    def roulette():
        return (scraper.get("https://rest-bf.blox.land/games/roulette").json()
                ["current"]["_id"])

    def jackpot():
        return (scraper.get("https://rest-bf.blox.land/games/jackpot").json()
                ["current"]["_id"])


class Crash:

    def test(self) -> None:
        return (scraper.get("https://rest-bf.blox.land/games/crash")).json()

    def gameCommitedEosBlock():
        return (scraper.get("https://rest-bf.blox.land/games/crash")
                ).json()["current"]["commitedEosBlock"]

    def gameRoundID():
        return (scraper.get("https://rest-bf.blox.land/games/crash")
                ).json()["current"]["_id"]

    def gamePublicSeed():
        return (scraper.get("https://rest-bf.blox.land/games/crash")
                ).json()["current"]["publicSeed"]

    def gamePrivateSeed():
        return (scraper.get("https://rest-bf.blox.land/games/crash")
                ).json()["current"]["privateHash"]


class Roulette:

    def test(self) -> None:
        return (scraper.get("https://rest-bf.blox.land/games/roulette")).json()

    def gameRoundID():
        return (scraper.get("https://rest-bf.blox.land/games/roulette")
                ).json()["current"]["_id"]

    def gamePublicSeed():
        return (scraper.get("https://rest-bf.blox.land/games/roulette")
                ).json()["current"]["publicSeed"]

    def gamePrivateSeed():
        return (scraper.get("https://rest-bf.blox.land/games/roulette")
                ).json()["current"]["privateHash"]


class click:
  def __init__(self, auth: str) -> None:
    self.auth = auth

  def mines(self, spot, no_game_message=None, invalid_auth_message=None, successfully_started_clicked_message=None) -> None:
    r = scraper.get("https://rest-bf.blox.land/user", headers={"x-auth-token": self.auth}).json()
    if not r["success"]:
      return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
    else:
      url = scraper.get("https://rest-bf.blox.land/games/mines", headers={"x-auth-token": self.auth}).json()
      if url["hasGame"] == False and no_game_message == None:
        return "User has no active game"
      else:
        if url["hasGame"] == False and no_game_message != None:
          return no_game_message
        else:
          if successfully_started_clicked_message == None:
            json = {
            "cashout": False,
            "mine": spot
          }
            url = "https://rest-bf.blox.land/games/mines/action"
            headers = {"x-auth-token": self.auth}
            data = scraper.post(url, headers=headers, json=json).json()
            return f"Successfully clicked {spot}."
          else:
            if successfully_started_clicked_message != None:
              json = {
            "cashout": False,
            "mine": spot
          }
              url = "https://rest-bf.blox.land/games/mines/action"
              headers = {"x-auth-token": self.auth}
              data = scraper.post(url, headers=headers, json=json)
              return successfully_started_clicked_message

  def towers(self, spot, no_game_message=None, invalid_auth_message=None, successfully_started_clicked_message=None) -> None:
    r = scraper.get("https://rest-bf.blox.land/user", headers={"x-auth-token": self.auth}).json()
    if not r["success"]:
      return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
    else:
      url = scraper.get("https://rest-bf.blox.land/games/towers", headers={"x-auth-token": self.auth}).json()
      if url["hasGame"] == False and no_game_message == None:
        return "User has no active game"
      else:
        if url["hasGame"] == False and no_game_message != None:
          return no_game_message
        else:
          if successfully_started_clicked_message == None:
            json = {
            "cashout": False,
            "tile": spot
          }
            url = "https://rest-bf.blox.land/games/towers/action"
            headers = {"x-auth-token": self.auth}
            data = scraper.post(url, headers=headers, json=json).json()
            return f'Successfully clicked {spot}'
          else:
            if successfully_started_clicked_message != None:
              json = {
            "cashout": False,
            "tile": spot
          }
              url = "https://rest-bf.blox.land/games/towers/action"
              headers = {"x-auth-token": self.auth}
              data = scraper.post(url, headers=headers, json=json).json()
              return successfully_started_clicked_message

  def mines_cashout(self, invalid_auth_message=None, no_game_message=None, game_ended_message=None) -> None:
    r = scraper.get("https://rest-bf.blox.land/user", headers={"x-auth-token": self.auth}).json()
    if not r["success"]:
      return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
    else:
      url = scraper.get("https://rest-bf.blox.land/games/mines", headers={"x-auth-token": self.auth}).json() 
      if url["hasGame"] == False and no_game_message == None:
        return "User has no active game"
      else:
        if url["hasGame"] == False and no_game_message != None:
          return no_game_message
        else:
          if game_ended_message == None:
            response = scraper.post("https://rest-bf.blox.land/games/mines/action", headers={
                            "x-auth-token": self.auth
                        },
                        json={
                            "cashout": True
                        }
                    ).json()
            return "Game has been ended"
          else:
                      if game_ended_message != None:
                        response = scraper.post("https://rest-bf.blox.land/games/mines/action", headers={
                            "x-auth-token": self.auth
                        },
                        json={
                            "cashout": True
                        }
                    ).json()
                        return game_ended_message
          

  def towers_cashout(self, invalid_auth_message=None, no_game_message=None, game_ended_message=None) -> None:
    r = scraper.get("https://rest-bf.blox.land/user", headers={"x-auth-token": self.auth}).json()
    if not r["success"]:
      return "User's auth is invalid" if invalid_auth_message is None else invalid_auth_message
    else:
      url = scraper.get("https://rest-bf.blox.land/games/towers", headers={"x-auth-token": self.auth}).json() 
      if url["hasGame"] == False and no_game_message == None:
        return "User has no active game"
      else:
        if url["hasGame"] == False and no_game_message != None:
          return no_game_message
        else:
          if game_ended_message == None:
            response = scraper.post("https://rest-bf.blox.land/games/towers/action", headers={
                            "x-auth-token": self.auth
                        },
                        json={
                            "cashout": True
                        }
                    ).json()
            return "Game has been ended"
          else:
                      if game_ended_message != None:
                        response = scraper.post("https://rest-bf.blox.land/games/towers/action", headers={
                            "x-auth-token": self.auth
                        },
                        json={
                            "cashout": True
                        }
                    ).json()
                        return game_ended_message