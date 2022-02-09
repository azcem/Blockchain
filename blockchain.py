from hashlib import sha256
import json
from random import randint
import time


def generate_transactions(n):
    transactions = []
    for i in range(n):
        transactions.append(randint(0, 2 ** 32-1))
    return transactions

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.branch = []
        self.create_genesis_block()
 
    def create_genesis_block(self):
        genesis_block = Block(0, generate_transactions(3), time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    difficulty = 1
    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash
    
    def tune(self):
        t_old = 0
        while True:
            t1 = time.time()
            self.proof_of_work(self.chain[0])
            t2 = time.time()
            t = round(t2-t1, 3)
            print(f'n = {Blockchain.difficulty}: t = {t}')
            if t > 1:
                #pick the time closest to 1
                if abs(t - 1) > abs(t_old - 1):
                    Blockchain.difficulty -= 1
                    return t_old
                else:
                    return t
            else:
                t_old = t
                Blockchain.difficulty += 1

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        #branch
        branch = False
        if previous_hash != block.previous_hash:
            branch = True
            if self.branch == []:
                for _block in self.chain:
                    if block.previous_hash == _block.previous_hash: break
                    self.branch.append(_block)
                    

        if not self.is_valid_proof(block, proof):
            return False, False

        block.hash = proof
        if branch:
            self.branch.append(block)
            #trust branch
            if len(self.branch) > len(self.chain) + 2:
                self.chain = self.branch
                self.branch = []
                return True, True
        else:
            self.chain.append(block)
        return True, False
 
    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    def add_new_transaction(self, transaction):
        if isinstance(transaction, list):
            self.unconfirmed_transactions.extend(transaction)
        else:
            self.unconfirmed_transactions.append(transaction)
    
    def mine(self):
            if not self.unconfirmed_transactions:
                return False
    
            last_block = self.last_block
    
            new_block = Block(index=last_block.index + 1,
                            transactions=self.unconfirmed_transactions,
                            timestamp=time.time(),
                            previous_hash=last_block.hash)
    
            proof = self.proof_of_work(new_block)
            _, branch = self.add_block(new_block, proof)
            self.unconfirmed_transactions = []
            return new_block.index, branch
    
    def print(self):
        print('<previous hash | Block no. | block hash>')
        for i in range(len(self.chain)):
            block = self.chain[i]
            print(f'<{block.previous_hash} | Block {i} | {block.hash}>')


def create_Block(n):
    t = generate_transactions(n)
    blockchain.add_new_transaction(t)

#INITIALIZING BLOCKCHAIN
blockchain = Blockchain()
t_mine = blockchain.tune()
print(f'blocks are generated at a rate of one block per {t_mine} seconds')
n = int(input('enter number of blocks in blockchain: (minimum 1) '))
for i in range(n-1):
    create_Block(3)
    blockchain.mine()
print(f'blockchain now has {n} blocks')
blockchain.print()

#ATTACKING
def attack(ind):
    if ind >= len(blockchain.chain): return False
    k = 0
    t1 = time.time()
    while True:
        branch_block = blockchain.chain[ind]
        new_block = Block(ind+1, generate_transactions(3), time.time(),branch_block.hash)
        proof = blockchain.proof_of_work(new_block)
        _, branch = blockchain.add_block(new_block, proof)
        k += 1
        if branch: break
    t2 = time.time()
    speed = round(t2 - t1, 4) / k
    return speed, k, round(t2-t1, 4)

n = int(input('determine block index for attack: '))
speed, k, t = attack(n)
print(f'{k} blocks are generated in {t} seconds, the attack speed is one block every {speed} seconds')
blockchain.print()

