class StateManager:
    # This function is started when the code start, such that every time the code is run, the 
    def __init__(self):
        self.initA = 0
        self.initB = 0
        self.initC = 0
        self.initE = 0
        self.initF = 0
        self.initG = 0
        self.initH = 0
        self.prev_state = None
        self.prev_turnSkipped = None
        self.initRST = False


    def functions_reset(self, n_state, n_turnSkipped):
        # If the state of the current state does not equal the previous state, then the state will be updated to being that state
        if n_state != self.prev_state:
            self.initRST = True
            self.prev_state = n_state

        # If a turn is skipped, the number of turns that have been skipped will be updated here.
        if n_turnSkipped != self.prev_turnSkipped:
            self.initRST = True
            self.prev_turnSkipped = n_turnSkipped

        # If there was a switch in state number, then this initRST becomes TRUE, and this it needs to restart all the tests that are necessary
        if self.initRST:
            print("A state transition or a turn-skip took place, the tests will be reset.")
            self.initA = 0
            self.initB = 0
            self.initC = 0
            self.initE = 0
            self.initF = 0
            self.initG = 0
            self.initH = 0
            self.initRST = False

        return n_state