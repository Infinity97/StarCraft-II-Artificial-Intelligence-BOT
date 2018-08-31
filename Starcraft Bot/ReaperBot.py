import sc2

import random
from collections import defaultdict

from sc2.constants import *

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.helpers import ControlGroup
weight = [1,1,1]
    

class RolloutBot(sc2.BotAI):
    def __init__(self, weights):
        self.SCV_counter = 0
        self.refinerys = 0
        self.barracks_started = False
        self.made_workers_for_gas = False
        self.attack_groups = set()
        self.reaper_health = {}
        self.enemy_health = {}
        self.reapergenes = defaultdict(list)
        self.reaperrewards = {}
        self.reaperindexer = {}
        self.weights = weights
        self.reaperlasttarget = {}
        self.reaperlasttargethealth = {}
        self.popmaker = 0
        
    async def on_step(self, iteration):
        if iteration == 0:
            if iteration == 0:
                await self.chat_send("(glhf)")

#for selecting our Units
        
        if self.units(REAPER).idle.amount > 15:
            for reaper in self.units(REAPER).idle:
                #Making the initial population for the first 10 reapers
                if reaper.tag in self.reapergenes:
                    print("already done")
                else:
                    if len(self.reaperrewards.values()) > 2:
                        v = list(self.reaperrewards.values())
                        k = list(self.reaperrewards.keys())
                        curmax = 0
                        for i in range(10):
                            pick = random.randint(0,len(v)-1)
                            if(v[pick] >= curmax):
                                curmax = v[pick]
                                curpick = k[pick]
                        
                        self.reapergenes[reaper.tag] = [0,0,0]       
                        self.reapergenes[reaper.tag][0] = self.reapergenes[curpick][0]
                        self.reapergenes[reaper.tag][1] = self.reapergenes[curpick][1]
                        self.reapergenes[reaper.tag][2] = self.reapergenes[curpick][2]
                       
                        
                        if random.randint(1,100)/100 <= .50:
                            print("mutate")
                            print([reaper.tag, self.reapergenes[reaper.tag], "Son of:", curpick, self.reapergenes[curpick] ,self.reaperrewards[curpick]])
                            #mutate
                            pick = random.randint(0,2)
                            if(random.randint(1,2) == 1):
                                print("minus .1")
                                self.reapergenes[reaper.tag][pick] -= .3
                            else:
                                print("plus .1")
                                self.reapergenes[reaper.tag][pick] += .3
                        
                        print([reaper.tag, self.reapergenes[reaper.tag], "Son of:", curpick, self.reapergenes[curpick] ,self.reaperrewards[curpick]])
                    else: #since there are no rewarded reapers
                        seed = [0,0,0]
                        
                        seed[0] = (random.randint(1,100)/100)
                        seed[1] = (random.randint(1,100)/100)
                        seed[2] = (random.randint(1,100)/100)
                        self.reapergenes[reaper.tag] = seed
                    

                                
                        #del v[v.index(max(v))]
            print(self.reapergenes)
        
                    
            cg = ControlGroup(self.units(REAPER).idle)
            self.attack_groups.add(cg)
            
        for cc in self.units(UnitTypeId.COMMANDCENTER).ready.noqueue:    
            if self.can_afford(SCV) and self.workers.amount < 20 and cc.noqueue:
                await self.do(cc.train(SCV))
        
        cc = self.units(COMMANDCENTER).ready.first
        bobthebuilder = self.units(SCV)[0]
        
#We must construct additional pylons
        if self.supply_left < 2:
            if self.can_afford(SUPPLYDEPOT) and self.already_pending(SUPPLYDEPOT) < 2:
                await self.build(SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 5))
        
#For building reapers     
        if self.units(BARRACKS).amount < 3 or (self.minerals > 400 and self.units(BARRACKS).amount < 5):
            if self.can_afford(BARRACKS):
                err = await self.build(BARRACKS, near=cc.position.towards(self.game_info.map_center, 5))      
           
        elif self.units(BARRACKS).ready.exists and self.units(REFINERY).ready.exists:
            barracks = self.units(BARRACKS).ready
            if self.can_afford(REAPER) and barracks.noqueue:
                await self.do(barracks.random.train(REAPER))
        
        '''
        if self.units(MISSILETURRET).amount < 3:
            if self.can_afford(MISSILETURRET):
                err = await self.build(MISSILETURRET, near=cc.position.towards(self.game_info.map_center, 5))  
        
        if self.units(ENGINEERINGBAY).amount < 1:
            if self.can_afford(ENGINEERINGBAY):
                err = await self.build(ENGINEERINGBAY, near=cc.position.towards(self.game_info.map_center, 5))        
        '''
        if self.refinerys < 2:
            if self.can_afford(REFINERY):
                worker = self.workers.random
                target = self.state.vespene_geyser.closest_to(worker.position)
                err = await self.do(bobthebuilder.build(REFINERY, target))
                if not err:
                    self.refinerys += 1
        
        for a in self.units(REFINERY):
            if a.assigned_harvesters < a.ideal_harvesters:
                w = self.workers.closer_than(20, a)
                if w.exists:
                    await self.do(w.random.gather(a))
        
        #TODO hash the reapers with info on health wieghts
        #TODO hash the enemy health totals to reward focusing
        #TODO reward reaper health maximization by hashing reaper health changes
        #TODO Create population
        #genes relevant to reaper movement
        #reaper attack allocation
            #weight for 
        #
        #
        barracks = self.units(BARRACKS).ready            
        for ac in list(self.attack_groups):
            alive_units = ac.select_units(self.units)
            total_x = []
            total_y = []
            total_z = []
            if alive_units.amount > 10:
                #Calculating which units are better to attack
                for reaper in ac.select_units(self.units):
                
                        
                    ting = 10
                    targets = self.known_enemy_units.prefer_close_to(reaper)
                    self.enemyreward = {}
                    self.enemyindexer = {}
                    for enemy in targets:
                        if ting == 0:
                            break
                        
                        self.enemyindexer[enemy.tag] = enemy
                        #the negative 1 gives more reward for enemies that are easily killed by your team/
                        if reaper.tag in self.reapergenes:
                            self.enemyreward[enemy.tag] = -1*(enemy.health-alive_units.amount*8)*self.reapergenes[reaper.tag][1]
                        #since they are already in order of closeness we can add a value for being closest
                        #and decrement it each time to give different rewards
                            self.enemyreward[enemy.tag] += self.reapergenes[reaper.tag][2]*(ting)
                        
                        ting -= 1
                
                
                if len(self.enemyreward.values()) > 0:
                    v = list(self.enemyreward.values())
                    k = list(self.enemyreward.keys())
                    
                    selectedtarget = self.enemyindexer[k[v.index(max(v))]]
                    target = selectedtarget.position
                else:
                    enemystart = 1
                    target = self.enemy_start_locations[0]
                
                #For loop deciding what a reaper should do
                for reaper in ac.select_units(self.units):
                    
                    
                    if reaper.tag in self.reaper_health and reaper.tag in self.reapergenes:
                        #If you've been hit kite away towards a safe place based on your genes
                        if  reaper.health < self.reaper_health[reaper.tag]:
                            await self.do(reaper.move(reaper.position.towards(barracks.random.position, self.reapergenes[reaper.tag][2]*10)))
                        
                        #if you are too injured to fight, run away
                        elif reaper.health < reaper.health_max*.4:
                            await self.do(reaper.move(barracks.random.position))
                        #if you aren't attacking or running you have to fight
                        elif reaper.is_idle:
                            await self.do(reaper.attack(target))
                    
                    #Setting up a reward slot for new reapers
                    if reaper.tag not in self.reaper_health:
                        self.reaperrewards[reaper.tag] = 0;
                    
                    #rewarding reapers for taking damage and surviving it        
                    if reaper.tag in self.reaper_health:        
                        self.reaperrewards[reaper.tag] += 60 - reaper.health
                    
                    #rewarding reapers for Killing units
                    if reaper.tag in self.reaperlasttarget:
                        #reward for a unit killed
                        if not self.reaperlasttarget[reaper.tag].health > 0:
                            self.reaperrewards[reaper.tag] += 2000
                            del self.reaperlasttarget[reaper.tag]
                        #reward for a unit maimed
                        elif self.reaperlasttarget[reaper.tag].health < self.reaperlasttargethealth[reaper.tag]:
                            self.reaperrewards[reaper.tag] += .1*(self.reaperlasttargethealth[reaper.tag] - self.reaperlasttarget[reaper.tag].health)
                    
                    #resetting sentinel dictionaries
                    if len(self.enemyreward.values()) > 0:    
                        self.reaperlasttarget[reaper.tag] = selectedtarget
                        self.reaperlasttargethealth[reaper.tag] = selectedtarget.health
                        self.reaper_health[reaper.tag] = reaper.health
            #if we don't have enough units to feasably continue the fight run back home
            else:
                for reaper in ac.select_units(self.units):
                    await self.do(reaper.move(cc.position))
                self.attack_groups.remove(ac)
                
        
        
run_game(maps.get("Simple64"), [
	Bot(Race.Terran, RolloutBot([1,1,1])),
	Computer(Race.Protoss, Difficulty.Medium)
], realtime=False, save_replay_as="GeneticBotEASY2.SC2Replay")
