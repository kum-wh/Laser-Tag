import time
from PlayerState import PlayerStateBase
from Helper import Actions

class StateStaff(PlayerStateBase): # StateStaff inherits from PlayerStateBase
    # update the player statistics
    def update(self, pos_self, pos_opponent, action_self, action_opponent, action_opponent_is_valid):
        self.action = action_self

        # check if the shield has to be reduced
        if self.shield_time > 0: # check if shield is being deployed
            if action_self == Actions.shield:
                # invalid, cannot use a new shield
                pass
            # update shield time
            self.shield_time = max(self.shield_max_time-(time.time()-self.shield_start_time), 0) # shiled_time is time_remaining
        elif action_self == Actions.shield: # now no shield is being deployed
            # check if still got shield left
            if self.num_shield > 0:
                # use a new shield and update ...
                self.num_shield        -= 1
                self.shield_time        = self.shield_max_time
                self.shield_health      = self.shield_health_max
                self.shield_start_time  = time.time()

        # update shield HP
        if self.shield_time <= 0:
            self.shield_health = 0

        # check for harm
        if action_opponent_is_valid:
            if pos_self == 4 and pos_opponent != 4:
                # we are protected from harm
                pass
            else:
                hp_reduction = 0
                if action_opponent == Actions.shoot:
                    hp_reduction = self.bullet_hp
                elif action_opponent == Actions.grenade:
                    hp_reduction = self.grenade_hp
                    
                if self.shield_time > 0:
                    if self.shield_health > 0:
                        self.shield_health -= hp_reduction

                    if self.shield_health < 0:
                        # we lose health
                        hp_reduction = -1*self.shield_health
                        self.shield_health = 0
                    else:
                        hp_reduction = 0

                # change the health
                self.hp -= hp_reduction

                if self.hp <= 0:
                    # we are dead, rebirth
                    # two flgs, when both done then send
                    self.hp = self.max_hp
                    self.num_deaths += 1
                    self.hp         = self.max_hp
                    self.action     = action_self # after rebirth, my action is "previous" action? yes, only when everything is done then send JSON
                    self.bullets    = self.magazine_size
                    self.grenades   = self.max_grenades
                    self.shield_time = 0
                    self.shield_health = 0
                    self.num_shield = self.max_shields

        # check for reduction in ammo
        if action_self == Actions.shoot:
            self.bullets = max(0, self.bullets-1)

        if action_self == Actions.grenade:
            self.grenades = max(0, self.grenades-1)

        if action_self == Actions.reload:
            if self.bullets > 0:
                # invalid
                pass
            else:
                self.bullets = self.magazine_size

    def action_is_valid(self, action_self):
        ret = True # is_valid

        # check if the shield has to reduced
        if action_self == Actions.shield:
            if self.shield_time > 0:
                # invalid
                ret = False
        elif action_self == Actions.shoot:
            if self.bullets <= 0:
                # invalid
                ret = False

        elif action_self == Actions.grenade:
            if self.grenades <= 0:
                # invalid
                ret = False

        elif action_self == Actions.reload:
            if self.bullets > 0:
                # invalid
                ret = False

        return ret
