from commands import add

def score(connection):
    return connection.protocol.get_kill_count()

add(score)

def apply_script(protocol, connection, config):
    
    class TDMConnection(connection):
    
        def on_spawn(self, pos):
            self.send_chat(self.protocol.get_kill_count())
            return connection.on_spawn(self, pos)

        def on_flag_capture(self):
            result = connection.on_flag_capture(self)
            self.team.kills += self.protocol.intel_points
            self.protocol.check_end_game(self)
            return result
        
        def on_kill(self, killer):
            result = connection.on_kill(self, killer)
            self.protocol.check_end_game(killer)
            return result
            
    class TDMProtocol(protocol):

        kill_limit = config.get('kill_limit', 100)
        intel_points = config.get('intel_points', 10)
        game_mode = 'tdm'
    
        def get_kill_count(self):
            green_kills = self.green_team.kills
            blue_kills = self.blue_team.kills
            diff = green_kills - blue_kills
            if green_kills>blue_kills:
                return ("Green leads %s-%s (+%s, %s left). Playing to %s kills." %
                        (green_kills, blue_kills,
                        diff,
                        self.kill_limit - green_kills,
                        self.kill_limit))
            elif green_kills<blue_kills:
                return ("Blue leads %s-%s (+%s, %s left). Playing to %s kills." %
                        (blue_kills, green_kills,
                        -diff,
                        self.kill_limit - blue_kills,
                        self.kill_limit))
            else:
                return ("%s-%s, %s left. Playing to %s kills." %
                        (green_kills,
                         blue_kills,
                        self.kill_limit - green_kills,
                        self.kill_limit))
        
        def check_end_game(self, player):
            if self.green_team.kills>=self.kill_limit:
                self.send_chat("Green Team Wins, %s - %s" %
                               (self.green_team.kills, self.blue_team.kills))
                self.reset_game(player)
            elif self.blue_team.kills>=self.kill_limit:
                self.send_chat("Blue Team Wins, %s - %s" %
                               (self.blue_team.kills, self.green_team.kills))
                self.reset_game(player)        
    
    return TDMProtocol, TDMConnection