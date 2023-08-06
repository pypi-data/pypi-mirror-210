from typing import Optional, Union, List, Tuple
import array, math, fractions


class QFShor:
    """This class is inherited from Qiskit Shor Algorithm"""

    def __init__(self):
        self._factors = []
        self._total_counts = 0
        self._successful_counts = 0

    @property
    def factors(self) -> List[List[int]]:
        """returns factors"""
        return self._factors

    @factors.setter
    def factors(self, value: List[List[int]]) -> None:
        """set factors"""
        self._factors = value

    @property
    def total_counts(self) -> int:
        """returns total counts"""
        return self._total_counts

    @total_counts.setter
    def total_counts(self, value: int) -> None:
        """set total counts"""
        self._total_counts = value

    @property
    def successful_counts(self) -> int:
        """returns successful counts"""
        return self._successful_counts

    @successful_counts.setter
    def successful_counts(self, value: int) -> None:
        """set successful counts"""
        self._successful_counts = value

    def get_factors(self, N: int, a: int, measurement: str) -> Optional[List[int]]:
        """Inherited from Qiskit - Apply the continued fractions to find r and the gcd to find the desired factors."""
        x_final = int(measurement, 2)
        # logger.info("In decimal, x_final value for this result is: %s.", x_final)

        if x_final <= 0:
            fail_reason = "x_final value is <= 0, there are no continued fractions."
        else:
            fail_reason = None
            # logger.debug("Running continued fractions for this case.")

        # Calculate T and x/T
        T_upper = len(measurement)
        T = pow(2, T_upper)
        x_over_T = x_final / T

        # Cycle in which each iteration corresponds to putting one more term in the
        # calculation of the Continued Fraction (CF) of x/T

        # Initialize the first values according to CF rule
        i = 0
        b = array.array("i")
        t = array.array("f")

        b.append(math.floor(x_over_T))
        t.append(x_over_T - b[i])

        exponential = 0.0
        while i < N and fail_reason is None:
            # From the 2nd iteration onwards, calculate the new terms of the CF based
            # on the previous terms as the rule suggests
            if i > 0:
                b.append(math.floor(1 / t[i - 1]))
                t.append((1 / t[i - 1]) - b[i])  # type: ignore

            # Calculate the denominator of the CF using the known terms
            denominator = self.calculate_continued_fraction(b)

            # Increment i for next iteration
            i += 1

            if denominator % 2 == 1:
                # logger.debug("Odd denominator, will try next iteration of continued fractions.")
                continue

            # Denominator is even, try to get factors of N
            # Get the exponential a^(r/2)

            if denominator < 1000:
                exponential = pow(a, denominator / 2)

            # Check if the value is too big or not
            if exponential > 1000000000:
                fail_reason = "denominator of continued fraction is too big."
            else:
                # The value is not too big,
                # get the right values and do the proper gcd()
                putting_plus = int(exponential + 1)
                putting_minus = int(exponential - 1)
                one_factor = math.gcd(putting_plus, N)
                other_factor = math.gcd(putting_minus, N)

                # Check if the factors found are trivial factors or are the desired factors
                if any(factor in {1, N} for factor in (one_factor, other_factor)):
                    # logger.debug("Found just trivial factors, not good enough.")
                    # Check if the number has already been found,
                    # (use i - 1 because i was already incremented)
                    if t[i - 1] == 0:
                        fail_reason = (
                            "the continued fractions found exactly x_final/(2^(2n))."
                        )
                else:
                    # Successfully factorized N
                    return sorted((one_factor, other_factor))

        # Search for factors failed, write the reason for failure to the debug logs
        # print(
        #     "Cannot find factors from measurement %s because %s",
        #     measurement,
        #     fail_reason or "it took too many attempts.",
        # )
        return None

    def calculate_continued_fraction(self, b: array.array) -> int:
        """Calculate the continued fraction of x/T from the current terms of expansion b."""

        x_over_T = 0

        for i in reversed(range(len(b) - 1)):
            x_over_T = 1 / (b[i + 1] + x_over_T)

        x_over_T += b[0]

        # Get the denominator from the value obtained
        frac = fractions.Fraction(x_over_T).limit_denominator()

        # logger.debug("Approximation number %s of continued fractions:", len(b))
        # logger.debug("Numerator:%s \t\t Denominator: %s.", frac.numerator, frac.denominator)
        return frac.denominator
