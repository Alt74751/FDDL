import numpy as np
import collections
import csv


'''Virtual Cache'''

class AVGFCache(object):
    def __init__(self, size, window, freq_discount):
        self.capacity = size
        self.occupation = 0
        self.cache = {}
        self.cache_key_list = []
        self.cache_freq_list = []
        self.cache_size_list = []
        self.window = window
        self.freq_discount = freq_discount
 
    def get(self, key, window_freq):
        if key in self.cache_key_list:
            p = self.cache_key_list.index(key) + 1
        else:
            return 0
        return p
 
    def set(self, key, feature_list):
        avg_freq_ = (1 / (2 * feature_list[0] ** 0.5)) * (feature_list[1] + feature_list[2] * (self.window[0] / self.window[1]) * self.freq_discount + feature_list[3] * (self.window[0] / self.window[2]) * (self.freq_discount ** 2))
        if key in self.cache_key_list:
            feature_list_old = self.cache.pop(key)
            p = self.cache_key_list.index(key)
            del self.cache_key_list[p]
            del self.cache_freq_list[p]
            del self.cache_size_list[p]
            self.cache[key] = feature_list.copy()
            insert_flag = False
            cache_len = len(self.cache_key_list)
            if cache_len > 0:
                for i in range(cache_len):
                    if avg_freq_ >= self.cache_freq_list[i]:
                        self.cache_key_list.insert(i, key)
                        self.cache_freq_list.insert(i, avg_freq_)
                        self.cache_size_list.insert(i, feature_list[0])
                        insert_flag = True
                        p_new = i + 1
                        break
                if insert_flag == False:
                    self.cache_key_list.append(key)
                    self.cache_freq_list.append(avg_freq_)
                    self.cache_size_list.append(feature_list[0])
                    p_new = cache_len + 1
                insert_flag = False
            else:
                self.cache_key_list.append(key)
                self.cache_freq_list.append(avg_freq_)
                self.cache_size_list.append(feature_list[0])
                p_new = 1
        else:
            size = feature_list[0]
            if self.occupation + size > self.capacity:
                evict_item_list = []
                evict_item_index = -1
                while self.occupation + size > self.capacity:
                    self.occupation -= self.cache_size_list[evict_item_index]
                    evict_item_index -= 1
                evict_item_index += 1
                evict_item_keys = self.cache_key_list[evict_item_index:]
                evict_item_freqs = self.cache_freq_list[evict_item_index:]
                evict_item_sizes = self.cache_size_list[evict_item_index:]
                for k in evict_item_keys:
                    evict_item_list.append(self.cache.pop(k))
                self.cache_key_list = self.cache_key_list[:evict_item_index]
                self.cache_freq_list = self.cache_freq_list[:evict_item_index]
                self.cache_size_list = self.cache_size_list[:evict_item_index]
                self.cache[key] = feature_list.copy()
                self.occupation += size
                insert_flag = False
                cache_len = len(self.cache_freq_list)
                for i in range(cache_len):
                    if avg_freq_ >= self.cache_freq_list[i]:
                        self.cache_key_list.insert(i, key)
                        self.cache_freq_list.insert(i, avg_freq_)
                        self.cache_size_list.insert(i, feature_list[0])
                        insert_flag = True
                        p_new = i + 1
                        break
                if insert_flag == False:
                    self.cache_key_list.append(key)
                    self.cache_freq_list.append(avg_freq_)
                    self.cache_size_list.append(feature_list[0])
                    p_new = cache_len + 1
                insert_flag = False
                return [evict_item_list, evict_item_freqs, evict_item_sizes, p_new]
            else:
                self.cache[key] = feature_list.copy()
                self.occupation += size
                insert_flag = False
                cache_len = len(self.cache_freq_list)
                if cache_len > 0:
                    for i in range(cache_len):
                        if avg_freq_ >= self.cache_freq_list[i]:
                            self.cache_key_list.insert(i, key)
                            self.cache_freq_list.insert(i, avg_freq_)
                            self.cache_size_list.insert(i, feature_list[0])
                            insert_flag = True
                            p_new = i + 1
                            break
                    if insert_flag == False:
                        self.cache_key_list.append(key)
                        self.cache_freq_list.append(avg_freq_)
                        self.cache_size_list.append(feature_list[0])
                        p_new = cache_len + 1
                    insert_flag = False
                else:
                    self.cache_key_list.append(key)
                    self.cache_freq_list.append(avg_freq_)
                    self.cache_size_list.append(feature_list[0])
                    p_new = 1
        
        return [None, None, None, p_new]


'''Real Cache'''

class RealCache(object):
    def __init__(self, size):
        self.capacity = size
        self.occupation = 0
        self.cache = {}

    def get(self, key):
        if key in self.cache.keys():
            return [key, self.cache[key]]
        else:
            return None


'''Cache environment for each gateway'''

class CacheEnv(object):
    def __init__(self, config):
        '''Init cache environment'''
        super().__init__()
        self.env_name = 'CacheEnv'
        self.action_size = config["action_size"]
        self.action_dim = self.action_size
        self.state_size = config["state_size"]
        self.state_dim = self.state_size
        self.cache_size = config["cache_size"]
        self.window = config["window"]
        self.bins = config["bins"]
        self.gamma_r = config["gamma_r"]
        self.freq_discount = config["freq_discount"]
        self.r_constant = 0  # Default value
        self.pan = -1  # Default value
        self.miu_r = config["miu_r"]
        self.max_content_size = config["max_content_size"]

    def update_state(self, request, other_is_cached, is_cached, poi):  # Key features of request statistics and cache status, default settings
        '''Update the state space'''
        self.ori_state[0] = (self.cache_size - self.cache.occupation) / self.cache_size
        self.ori_state[1] = request[2] / self.max_content_size
        self.ori_state[2] = (request[4] / 3600) if (request[4] < 36000) else 10
        self.ori_state[2] /= 10
        self.ori_state[3] = (request[5] / 1000) if (request[5] < 10000) else 10
        self.ori_state[3] /= 10
        self.state[0] = np.digitize(self.ori_state[0], self.bins)
        self.state[1] = np.digitize(self.ori_state[1], self.bins)
        self.state[2] = np.digitize(self.ori_state[2], self.bins)
        self.state[3] = np.digitize(self.ori_state[3], self.bins)
        self.state[4] = request[6] if request[6] < 10 else 10
        self.state[5] = request[7] if request[7] < 10 else 10
        self.state[6] = request[8] if request[8] < 10 else 10
        self.state[7] = is_cached
        self.state[9] = np.digitize((len(self.cache.cache_key_list) - poi) / len(self.cache.cache_key_list), self.bins) if poi else 0
        self.state[8] = sum(other_is_cached) if sum(other_is_cached) < 10 else 10
        return self.state

    def step(self, action, request, other_is_cached):
        '''One step in DRL'''
        other_cache_flag = 1 if sum(other_is_cached) > 0 else 0
        other_cache_rate = sum(other_is_cached) / len(other_is_cached)
        if action:
            _, _, _, poi_new = self.cache.set(request[1], [request[2], request[6], request[7], request[8]])
            self.next_state = self.state.copy()
            self.next_state[0] = np.digitize((self.cache_size - self.cache.occupation) / self.cache_size, self.bins)
            self.next_state[7] = 1
            self.next_state[9] = np.digitize((len(self.cache.cache_key_list) - poi_new) / len(self.cache.cache_key_list), self.bins)
            self.reward = self.miu_r[0] * (self.state[4] + self.gamma_r * self.state[5] + self.gamma_r * self.gamma_r * self.state[6]) / (self.state[3] ** 2) - self.miu_r[1] * (request[2] / self.max_content_size) * (self.cache.occupation / self.cache_size) - (self.miu_r[2] * other_cache_flag + self.miu_r[3] * other_cache_rate) - self.miu_r[4] * self.r_constant
        else:
            self.next_state = self.state.copy()
            self.reward = self.pan * (self.miu_r[0] * (self.state[4] + self.gamma_r * self.state[5] + self.gamma_r * self.gamma_r * self.state[6]) / (self.state[3] ** 2) - self.miu_r[1] * (request[2] / self.max_content_size) * (self.cache.occupation / self.cache_size) - self.miu_r[4] * self.r_constant) + self.miu_r[2] * other_cache_flag + self.miu_r[3] * other_cache_rate
        done = False

        return self.next_state, self.reward, done, {}

    def reset(self):
        """Resets the environment"""
        self.ori_state = np.zeros(self.state_size)
        self.state = np.zeros(self.state_size)
        self.cache = AVGFCache(self.cache_size, self.window, self.freq_discount)
        self.real_cache = RealCache(self.cache_size)
        self.next_state = None
        self.action = None
        self.reward = None
        self.done = False
        return self.state
