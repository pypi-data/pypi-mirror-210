def get_lower_bound(positions: dict, theo_bound: int) -> int:
    lower_bound = 0
    for kmer, pos in positions.items():
        if int(kmer) > theo_bound:
            return lower_bound
        lower_bound = pos
