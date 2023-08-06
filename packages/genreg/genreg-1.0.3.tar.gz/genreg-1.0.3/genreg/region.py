# == MODULE region.py ==

"""
Genomic region module.
'Full' version, not to be shared with the participants.
:author: András Aszódi
:date: 2020-11-10
"""

import re

class Region:
    """
    Instances of the Region class represent genomic regions.
    A Region object stores a chromosome, start and end coordinates,
    an arbitrary region name, and a strand direction indicator.
    It can be converted to and from strings formatted as BED or GFF.
    """

    # 2. The initialiser
    def __init__(self, chrom="chrUn",
                 start=0, end=0,
                 name=".", score=0.0, strand="."):
        """
        Creates a new Region object.
        :param chrom: The chromosome name, default "chrUn" (by convention this means "unknown")
        :param start: The start coordinate. Always 0-based ("BED convention")
        :param end: The end coordinate. Half-open, BED convention.
            If `end` < `start` then they are swapped silently.
        :param name: The name of the region, can be an arbitrary string
        :param score: Some number, e.g. in BED files it is between 0 and 1000
        :param strand: Strand direction indicator, can be "+","-", or "." (the default).
            Only the first character of the parameter is used.
            Any other character will be converted to "." silently.
        """
        self.chrom = chrom
        if start > end:
            end, start = start, end
        self.start = start
        self.end = end
        self.name = name
        self.score = score
        s0 = strand[0]
        self.strand = s0 if s0 in "+-." else "."

    # -- Conversion from/to strings --

    # 3. Input
    def from_bed(self, line):
        """
        Parses a string according to the BED standard.
        If parsing is successful, update the calling object with the new values.
        :param line: A string, possibly a line read from a BED file.
        :return: True if parsing was successful and the calling object was modified,
            False if `line` was empty/all-whitespace/comment and the calling object was not changed.
        :raise: ValueError if parsing was unsuccessful
        """
        # 3A-1. Ignore "empty" lines
        if self._ignore_line(line):
            return False

        # 3B. Split line in fields
        fields = line.split("\t")
        flen = len(fields)
        if flen < 3:
            raise ValueError("Too few fields")

        # 3C-1. Parse input fields
        chrom = fields[0]
        start = int(fields[1])  # may raise ValueError
        end = int(fields[2])
        name = fields[3] if flen >= 4 else "."
        score = float(fields[4]) if flen >= 5 else 0.0
        strand = fields[5][0] if flen >= 6 else "."

        # 3C-2. Update calling object
        self.chrom = chrom
        # automatic swapping if start > end
        self.start, self.end = (start, end) if start <= end else (end, start)
        self.name = name
        self.score = score
        self.strand = strand if strand in "+-." else "."
        return True

    # HW
    def from_gff(self, line):
        """
        Parses a string according to the GFF standard.
        If parsing is successful, update the calling object with the new values.
        :param line: A string, possibly a line read from a GFF file.
        :return: True if parsing was successful and the calling object was modified,
            False if `line` was empty/all-whitespace/comment and the calling object was not changed.
        :raise: ValueError if parsing was unsuccessful
        """
        # Implementation is left as an exercise to the participants
        ### **TEACHER'S NOTE** : the "skel" version should contain a `pass` here
        # pass
        ### **TEACHER'S NOTE** : implementation
        # Ignore "empty" lines
        if self._ignore_line(line):
            return False

        # Split line in fields
        fields = line.split("\t")
        flen = len(fields)
        if flen < 5:
            raise ValueError("Too few fields")

        # Parse input fields
        chrom = fields[0]
        src = fields[1]  # "source" field: not stored
        name = fields[2]    # "feature" field
        start = int(fields[3]) - 1 # may raise ValueError: note silly GFF start offset convention
        end = int(fields[4])
        score = float(fields[5]) if flen >= 6 else 0.0
        strand = fields[6][0] if flen >= 7 else "."
        # ... ignore "frame" and "group" fields

        # Update calling object
        # Same as `from_bed()`, just repeated here
        self.chrom = chrom
        # automatic swapping if start > end
        self.start, self.end = (start, end) if start <= end else (end, start)
        self.name = name
        self.score = score
        self.strand = strand if strand in "+-." else "."
        return True
        ### **END**

    # 4. Output
    def to_gff(self, src="genreg"):
        """
        Converts a Region object to its GFF string representation.
        :param src: This string will be used as the value of the GFF source field
        :returns: The string representation according to the GFF specification.
        """
        return "\t".join( (
            self.chrom,
            src,     # the GFF source field
            self.name,
            str(self.start + 1),  # BED->GFF coordinate transformation
            str(self.end),
            str(self.score),
            self.strand,
            ".", ".",    # "frame" and "group" columns that we do not worry about
        ) )

    # HW
    def to_bed(self):
        """
        Converts a Region object to its BED string representation.
        :returns: The string representation according to the GFF specification.
        """
        # Implementation is left as an exercise to the participants
        ### **TEACHER'S NOTE** : the "skel" version should contain a `pass` here
        # pass
        ### **TEACHER'S NOTE** : implementation
        return "\t".join( (
            self.chrom,
            str(self.start),
            str(self.end),
            self.name,
            str(self.score),
            self.strand
        ) )

    # Examples of "special" methods
    # They always have two underscores at the beginning and end of their names.
    # The two methods below implement equality comparison for the Region class.
    # In our case it is really simple but in general you may have special requirements,
    # for instance when string members have to be compared in a case-insensitive manner.

    # 5. Equality
    def __eq__(self, other):
        """
        Two Regions are considered equal if all their attributes are equal.
        This method will be invoked in expressions like `if region1 == region2: ...`
        """

        # Use this idiom if all members are supposed to be the same.
        # The __dict__ special member lists all members of a class (or object)
        # in a dictionary.
        return type(other) is type(self) and \
               self.__dict__ == other.__dict__

    # Properties
    # You can invoke methods that have been decorated with `@property`
    # without the parentheses, imitating member access.

    # 6. Region size
    @property
    def size(self):
        """
        :return: The size (length) of the region.
        """
        return self.end - self.start

    # -- "private" methods --

    # There are no truly private (hidden) methods in Python.
    # Encapsulation (hiding of implementation details) can be emulated
    # by a naming convention: any data member or method is considered "private'
    # by convention if its name starts by an underscore.

    # 3A-2. Detects "empty" lines to be ignored by the input methods.
    def _ignore_line(self, line):
        """
        :param line: A string containing a line, possibly read from a BED or GFF file.
        :return: True if `line` is empty or all-whitespace or a comment.
        """
        return len(line) == 0 or \
            re.match(r"^[ \t]*$", line) or \
            line[0] == '#'

