def letter_grade(score):
    for cut, g in ((90, 'A'), (80, 'B'), (70, 'C'), (60, 'D')):
        if score >= cut:
            return g
    return 'F'
