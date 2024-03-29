"""
FIT3155 Assignment 2
Question 1: Suffix Tree to Suffix Array

Description:
A program that computes the suffix array of a given string str[1...n] by first
constructing its suffix tree and then generating a suffix array from it.

All input strings come from the ASCII range [37, 126].

Argument:
A filename, whose contents are the input string

Output: output_sa.txt
Contains the indexes corresponding to the suffix array of str[1...n], one per line

Author: Emily Zarry
ID: 32558945
"""
import sys


def write_file(filename: str, results: list):
    """
    Function to write the results to a file, will write each element of the list in a single line
    :param filename: file name we want to write the results to
    :param results: the list we want to write into the file
    :return: nothing
    """
    with open(filename, "w") as f:
        for result in results:
            f.write(str(result + 1) + "\n")


def read_file(file_path: str) -> str:
    """
    Function to read a file and return the first line
    :param file_path: the filepath we want to read the first line of
    :return: the first line of the file
    """
    with open(file_path, 'r') as f:
        line = f.readline()

    return line.strip()


class Node:
    """
    Node class for Ukkonen's suffix tree
    """
    global_end = -1

    def __init__(self, start, end, suffix_index,):
        self.start = start                      # Start point of edge connecting the node to its parent
        self.end = end                          # End point of edge connecting the node to its parent
        self.suffix_index = suffix_index        # Starting point of suffix ending at the node
        self.children = [None] * 127            # Children nodes connected to the node
        self.suffix_link = None                 # Suffix link of the node
        self.visited = False                    # For DFS traversal of the suffix tree when obtaining suffix array

    def is_leaf(self):
        return self.end is None                 # Node is a leaf if the end is set to None

    def get_end(self):
        if self.is_leaf():
            return Node.global_end              # If the node is a leaf, return the tree's global_end
        else:
            return self.end

    def get_edge_length(self):
        return self.get_end() - self.start + 1


def inc_global_end():
    Node.global_end += 1


def ukkonen_suffix_tree(txt: str) -> Node:
    """
    Function to generate a string's Ukkonen's suffix tree
    :param txt: the string we want to generate the suffix tree of
    :return: the tree's root node
    """
    # Append special end character $
    txt += "$"

    # Initialize root node
    root = Node(-1, -1, -1)
    root.suffix_link = root
    active_node = root

    # Initialize active data
    remainder = 0
    pending = None

    # Phase 1: Rule 2 Alternate
    inc_global_end()
    active_edge = ord(txt[0])
    active_node.children[ord(txt[0])] = Node(0, None, 0)
    last_j = 0

    for phase in range(1, len(txt)):
        # Rule 1
        inc_global_end()

        # Reset pending in each phase
        pending = None
        skipped_edge_length = 0

        # Go through each remaining extension (Either rule 2 or 3)
        j = last_j + 1      # Start from next j
        while j != phase + 1:
            if remainder == 0:
                active_edge = ord(txt[phase])

            # If no edge going out of active_node that matches active_edge
            if active_node.children[active_edge] is None:
                # Rule 2 Alternate: Hang new leaf on existing node
                active_node.children[active_edge] = Node(phase, None, j)

                # Update last_j
                last_j = j

                # Resolve pending
                if pending is not None:
                    pending.suffix_link = active_node
                    pending = None
            # If there is edge going out of active_node that matches active_edge
            else:
                next_node = active_node.children[active_edge]

                # Check if walk down is needed
                # If remainder is greater or equal to the edge length of the next node
                if remainder >= next_node.get_edge_length():
                    # Walk down
                    # Set active_edge as the next character in the path after skip/count trick
                    skipped_edge_length += next_node.get_edge_length()
                    active_edge = ord(txt[j + skipped_edge_length])

                    # Update remainder
                    remainder -= next_node.get_edge_length()

                    # Set next_node as active_node (Walk down)
                    active_node = next_node

                    # If walk down performed, continue extension at the next node
                    continue

                # Rule 3: Do nothing (Next character already exists in the path)
                if txt[phase] == txt[next_node.start + remainder]:
                    # Increment remainder
                    remainder += 1

                    # Resolve pending
                    if pending is not None and pending != root:
                        pending.suffix_link = active_node
                        pending = None

                    # Stop early and go to next phase
                    j = phase + 1
                    break

                # Rule 2 Regular: Create new internal node and hang new leaf off of it
                # Create new internal node
                # suffix_index is -2 if it is internal node
                new_node = Node(next_node.start, next_node.start + remainder - 1, -2)
                active_node.children[active_edge] = new_node

                # Hang new leaf off the new internal node
                new_node.children[ord(txt[phase])] = Node(phase, None, j)

                # Update remaining edge's start point
                next_node.start += remainder

                # Hang remaining edge to the new internal node
                new_node.children[ord(txt[next_node.start])] = next_node

                # Update last_j
                last_j = j

                # Resolve pending
                if pending is not None:
                    # The suffix link should point to the newly created internal node
                    pending.suffix_link = new_node

                    # Set pending to the new internal node
                    pending = new_node

                # Put the newly created internal node to pending (resolve its suffix link in the next extension)
                pending = new_node

            # End of extension
            # If active_node is root and remainder is not 0
            if active_node == root and remainder > 0:
                # Cut one character from the remainder
                remainder -= 1

                # Update active_edge
                active_edge = ord(txt[last_j + 1])
            # Else if active_node is not the root
            elif active_node != root:
                # Set its suffix link as the new active_node
                active_node = active_node.suffix_link

            # Increment j
            j += 1
            skipped_edge_length = 0

    return root


def get_suffix_array(root: Node) -> list:
    """
    Function to get a string's suffix array from its suffix tree
    :param root: the root node of the string's suffix tree
    :return: the string's suffix array
    """
    suffix_array = []

    def dfs(node: Node):
        if node.is_leaf():
            suffix_array.append(node.suffix_index)

        for child in node.children:
            if child is not None and not child.visited:
                child.visited = True
                dfs(child)

    dfs(root)

    return suffix_array


if __name__ == '__main__':
    _, filename = sys.argv
    string = read_file(filename)

    root = ukkonen_suffix_tree(string)

    write_file("output_sa.txt", get_suffix_array(root))
