from collections import deque, defaultdict

class AhoCorasick:
  def __init__(self):
    self.trie = {}
    self.fail = {}
    self.output = defaultdict(list)

  def add_word(self, word, value):
    """
    Add a word and its associated value to the trie.
    """
    node = self.trie
    for char in word:
      if char not in node:
        node[char] = {}
      node = node[char]
    node["_end"] = True
    self.output[id(node)].append(value)

  def build(self):
    """
    Build the failure links for the Aho-Corasick automaton.
    """
    queue = deque()

    # Initialize the root's children
    for char, child in self.trie.items():
      self.fail[id(child)] = self.trie
      queue.append(child)

    # BFS to build failure links for all nodes
    while queue:
      current_node = queue.popleft()
      for char, child in current_node.items():
        if char == "_end":
            continue
        # Set failure link for child
        fallback = self.fail[id(current_node)]
        while char not in fallback and fallback != self.trie:
          fallback = self.fail[id(fallback)]
        self.fail[id(child)] = fallback[char] if char in fallback else self.trie

        # Merge output from the fail link
        self.output[id(child)].extend(self.output[id(self.fail[id(child)])])

        queue.append(child)

  def search(self, text):
    """
    Search for all patterns in the text.
    Returns a list of matched values.
    """
    node = self.trie
    matches = []

    for char in text:
      # Follow failure links until a match or root is reached
      while char not in node and node != self.trie:
        node = self.fail[id(node)]

      # If the character matches, follow the trie
      if char in node:
        node = node[char]
      else:
        node = self.trie

      # Append matches from the current node
      matches.extend(self.output[id(node)])

    return matches

