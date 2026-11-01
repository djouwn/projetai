"""Part 1.1: LIFO Stack and FIFO Queue using two Stacks."""

#Stack is lifo and Queue is fifo
class Stack:
    #initialisation de la liste vide
    def __init__(self):
        self.data = []
    
    #adding an item to the list
    def push(self, x):
        self.data.append(x)
    #removing an item from the list if the list is not already empty, otherwise it raises an error
    def pop(self):
        if self.is_empty():
            raise IndexError("Empty stack")
        return self.data.pop()
    #returning the last item from the list if it is not already empty, otherwise it raises an error
    def top(self):
        if self.is_empty():
            raise IndexError("Empty stack")
        return self.data[-1]
    # checks if list is empty return type is boolean 
    def is_empty(self):
        return len(self.data) == 0
    # retunrs the length of the list
    def __len__(self):
        return len(self.data)


class Queue:
    def __init__(self):
        self.input_stack = Stack()
        self.output_stack = Stack()
    # add an item to the input queue
    def enqueue(self, x):
        self.input_stack.push(x)
    # remove an item from the output queue if it is not empty, otherwise it raises an error
    def dequeue(self):
        if self.output_stack.is_empty():
            while not self.input_stack.is_empty():
                x = self.input_stack.pop()
                self.output_stack.push(x)

        if self.output_stack.is_empty():
            raise IndexError("Empty queue")

        return self.output_stack.pop()
#checks if both input and output queues are empty, return type is boolean
    def is_empty(self):
        return self.input_stack.is_empty() and self.output_stack.is_empty()
#returns the length of both input and output queues
    def __len__(self):
        return len(self.input_stack) + len(self.output_stack)