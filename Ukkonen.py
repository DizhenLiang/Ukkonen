import sys

class EndMarker:
    def __init__(self):
        self.value = -1

    def increment(self):
        """Increment the value of the end marker."""
        self.value += 1

    def __str__(self):
        """Return the string representation of the end marker's value."""
        return str(self.value)

class TrieNode:
    def __init__(self, node_id=None, start_idx=None, end_idx=None, is_terminal=False):
        self.node_id = node_id
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.is_terminal = is_terminal
        self.children = [None] * 91  # ASCII printable characters from 36 to 126
        self.suffix_link = None

    def get_child_at(self, char_pos):
        return self.children[char_pos]

    def add_child(self, char_pos, new_child):
        self.children[char_pos] = new_child

    def end_index(self):
        if self.is_terminal:
            return EndMarker().value  # Return the global end value for terminal nodes
        else:
            return self.end_idx

    def __repr__(self):
        return f"TrieNode(start={self.start_idx}, end={self.end_idx})"

class UkkonenSuffixTree:
    """
    Builds the suffix tree using Ukkonen's algorithm.
    """
    def __init__(self, input_str):
        """
        Initialize the suffix tree with the given input string.
        """
        self.input_str = input_str + "$"  
        self.root = TrieNode(node_id=-1)
        self.root.suffix_link = self.root  # Suffix link trick
        self.active_length = 0
        self.active_edge = None
        self.active_node = self.root
        self.global_end_marker = EndMarker()  # Global end marker for terminal nodes
        self.suffix_ids = []
        self.build_suffix_tree()
        self.retrieve_suffix_ids(self.root)

    def build_suffix_tree(self):
        """Apply Ukkonen's algorithm rules to build the suffix tree."""
        j = 0
        for i in range(len(self.input_str) + 1):  # For each extension
            self.global_end_marker.increment()  # Rule 1: Extend the active leaf
            last_internal_node = None  # Suffix link handling

            while j < i:
                if self.active_node == self.root:
                    self.active_length = i - j  # Reset active length

                next_node = self.traverse_path(self.active_node, self.active_length)

                # Get the child node for the next character in the input string
                char_pos = ord(self.input_str[i - self.active_length]) - 36
                active_edge = self.active_node.get_child_at(char_pos)

                if not active_edge:
                    # Rule 2.1: No path for character, create new leaf
                    # active node -> leaf edge
                    new_leaf = TrieNode(node_id=j, start_idx=i - self.active_length, end_idx=self.global_end_marker.value, is_terminal=True)
                    self.active_node.add_child(char_pos, new_leaf)
                elif self.input_str[i - 1] != self.input_str[active_edge.start_idx + self.active_length - 1]:
                    # Rule 2.2: Split the edge and create a new internal node
                    # from: active node -> leaf
                    #   to: active node -. internal node -> leaf
                    new_internal = TrieNode(node_id=ord(self.input_str[i - 1]), start_idx=active_edge.start_idx, end_idx=active_edge.start_idx + self.active_length - 1, is_terminal=False)
                    self.active_node.add_child(char_pos, new_internal)
                    #Do not create new active edge, otherwise childs lost
                    active_edge.start_idx += self.active_length - 1
                    new_internal.add_child(ord(self.input_str[active_edge.start_idx]) - 36, active_edge)

                    # Create new leaf node
                    new_leaf = TrieNode(node_id=j, start_idx=i - 1, end_idx=self.global_end_marker.value, is_terminal=True)
                    new_internal.add_child(ord(self.input_str[i - 1]) - 36, new_leaf)

                    # Update suffix links
                    new_internal.suffix_link = self.root
                    if last_internal_node:
                        last_internal_node.suffix_link = new_internal
                    last_internal_node = new_internal
                else:
                    # Rule 3: Path already exists, do nothing (Show-Stopper trick)
                    # the characters in the edge = char in string
                    break

                j += 1
                self.active_node = self.active_node.suffix_link
                self.active_length += 1

    def traverse_path(self, current_node, length):
        """Traverse the path using the skip/-count trick.
            to update the active node 
        """
        if current_node.is_terminal or length == 0:
            return current_node

        current_node = self.active_node
        active_length = length

        # Traverse the edge
        char_pos = ord(self.input_str[self.global_end_marker.value - active_length]) - 36
        edge_node = current_node.get_child_at(char_pos)

        if not edge_node:
            return current_node
        else:
            edge_len = edge_node.end_index() - edge_node.start_idx
            if edge_len > active_length:
                return current_node

        return self.traverse_path(edge_node, active_length - edge_len)


    def retrieve_suffix_ids(self, node):
        """
        Inorder traversal to retrieve suffix IDs for each leaf node.
        """
        if not node:
            return
        elif node.is_terminal:
            self.suffix_ids.append(node.node_id)
        else:
            for child in node.children:
                if child:
                    self.retrieve_suffix_ids(child)


def read_file(filename):
    """Read the contents of the file."""
    with open(filename, 'r') as file:
        return file.read()

# Rest of the script to read files and write the output remains the same

def write_to_output(filename, ranks):

    with open(filename, 'w') as file:
        for rank in ranks:
            file.write(f"{rank}\n")

def main(string_filename, positions_filename):
    # Read the input string and positions from the files
    input_string = read_file(string_filename)
    positions_str = read_file(positions_filename)
    positions = [int(pos) for pos in positions_str.strip().split('\n')] 
    #input_string = "mississippi$"  

    uk = UkkonenSuffixTree(input_string)
    #suffix_ids = [11, 10, 7, 4, 1, 0, 9, 8, 6, 3, 5, 2]
    suffix_ids = uk.suffix_ids
    #print(suffix_ids)

    suffix_dict = {}
    for i in range(len(suffix_ids)):
        suffix_dict[suffix_ids[i]] = i+1

    #print(suffix_dict)
    sorted_dict = dict(sorted(suffix_dict.items(), key=lambda item: item[0]))
    #print(sorted_dict)
    #input_arr = [2,8,10,6,7]
    res = []

    for num in positions:
        ind = sorted_dict[num-1]
        res.append(ind)
        #print(ind)

    # Write the ranks to the output file
    write_to_output('output_q1.txt', res)


if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        #print("Usage: python q1.py <stringFileName> <positionsFileName>")
        sys.exit(1)

    string_filename = sys.argv[1]
    positions_filename = sys.argv[2]
    main(string_filename, positions_filename)