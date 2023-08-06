## Lehmers Random Number Generator
lehmers_vars = {  # Xn+1 = a*Xn + c mod m
    "a": None,  # Multiplier
    "c": None,  # Increment
    "m": None,  # Modulus
    "x": None,  # Seed/Current Value
}


def clear_lehmers_vars():
    """
    This function clears the global dictionary lehmersVars
    """
    global lehmers_vars
    lehmers_vars = {  # Xn+1 = a*Xn + c mod m
        "a": None,  # Multiplier
        "c": None,  # Increment
        "m": None,  # Modulus
        "x": None,  # Seed/Current Value
    }


def lehmers_init(a, c, m, x):
    """
    This function initializes the parameters for the Lehmer's Random Number Generator

    Parameters
    ----------
    a : int
        The multiplier
    c : int
        The increment
    m : int
        The modulus
    x : int
        The seed

    Returns
    -------
    None
    """
    global lehmers_vars
    # Set the values for the global dictionary lehmersVars
    lehmers_vars["a"] = a
    lehmers_vars["c"] = c
    lehmers_vars["m"] = m
    lehmers_vars["x"] = x


def lehmers_rand(a=None, c=None, m=None, x=None):
    """
    This function generates a random number using Lehmer's Random Number Generator. It takes in 4 optional parameters a, c, m, x which can be used to initialize the generator

    Parameters
    ----------
    a : int, optional
        The multiplier
    c : int, optional
        The increment
    m : int, optional
        The modulus
    x : int, optional
        The seed

    Returns
    -------
    float
        A random number between 0 and 1
    """
    global lehmers_vars
    # Check if the generator has been initialized, if not, use default values to initialize it
    if (
        lehmers_vars["a"] == None
        or lehmers_vars["c"] == None
        or lehmers_vars["m"] == None
        or lehmers_vars["x"] == None
    ):
        if a == None or c == None or m == None or x == None:
            # Initialize the generator with default values
            lehmers_init(7**5, 0, 2**31 - 1, 1.0)
            # Print out the initialized values
            print(
                f'Lehmers Random Number Generator Initialized with default values\n\ta={lehmers_vars["a"]}\n\tc={lehmers_vars["c"]}\n\tm={lehmers_vars["m"]}\n\tx={lehmers_vars["x"]}'
            )
        else:
            # Initialize the generator with the given values
            lehmers_init(a, c, m, x)
    # Generate a random number using Lehmer's formula
    lehmers_vars["x"] = (
        lehmers_vars["a"] * lehmers_vars["x"] + lehmers_vars["c"]
    ) % lehmers_vars["m"]
    # Return the generated random number
    return lehmers_vars["x"] / lehmers_vars["m"]


# Marsaglia's Random Number Generator: Subtract with Borrow
marsaglia_vars = {  # f(x_1...x_r,c) =    | (x_2,...,x_r, x_1-x_{r-s} - c , 0)      if x_1-x_{r-s} - c >= 0
    #                     | (x_2,...,x_r, x_1-x_{r-s} - c + b, 1)   if x_1-x_{r-s} - c < 0
    "base": None,  # Base
    "lag_r": None,  # Lag r
    "lag_s": None,  # Lag s
    "carry": None,  # Carry
    "args": None,  # Values of x_1...x_r
}


def clear_marsaglia_vars():
    """
    This function clears the global dictionary marsagliaVars
    """
    global marsaglia_vars
    marsaglia_vars = {  # f(x_1...x_r,c) =    | (x_2,...,x_r, x_1-x_{r-s} - c , 0)      if x_1-x_{r-s} - c >= 0
        #                     | (x_2,...,x_r, x_1-x_{r-s} - c + b, 1)   if x_1-x_{r-s} - c < 0
        "base": None,  # Base
        "lag_r": None,  # Lag r
        "lag_s": None,  # Lag s
        "carry": None,  # Carry
        "args": None,  # Values of x_1...x_r
    }


def marsaglia_init(base, lag_r, lag_s, carry, seed_tuple):
    """
    This function initializes the parameters for the Marsaglia's Random Number Generator

    Parameters
    ----------
    base : int
        The base
    lag_r : int
        The lag r
    lag_s : int
        The lag s
    carry : int
        The carry
    seed_tuple : tuple
        The seed tuple

    Returns
    -------
    None
    """

    global marsaglia_vars
    if (
        type(seed_tuple) == tuple and len(list(seed_tuple)) != 2
    ):  # Check if the seed_tuple is of length 2
        raise ValueError("seed_tuple must be a tuple of length 2")
    elif type(seed_tuple) != tuple:  # Check if the seed_tuple is a tuple
        raise ValueError("seed_tuple must be a tuple ")
    if lag_r < 1 or lag_s < 1:  # Check if lag_r and lag_s are greater than 0
        raise ValueError("lag_r and lag_s must be greater than 0")
    if lag_r < lag_s:  # Check if lag_r is greater than or equal to lag_s
        raise ValueError("lag_r must be greater than or equal to lag_s")
    if carry < 0 or carry > 1:  # Check if carry is 0 or 1
        raise ValueError("carry must be 0 or 1")
    if base < 1:  # Check if base is greater than 0
        raise ValueError("base must be greater than 0")
    # Set the values for the global dictionary marsagliaVars
    marsaglia_vars["base"] = base
    marsaglia_vars["lag_r"] = lag_r
    marsaglia_vars["lag_s"] = lag_s
    marsaglia_vars["carry"] = carry
    marsaglia_vars["args"] = [0] * lag_r
    marsaglia_vars["args"][0] = seed_tuple[
        0
    ]  # Set the value of x_1 to the first element of the seed_tuple
    marsaglia_vars["args"][lag_r - lag_s] = seed_tuple[
        1
    ]  # Set the value of x_{r-s} to the second element of the seed_tuple


def marsaglia_rand(base=None, lag_r=None, lag_s=None, carry=None, seed_tuple=None):
    """
    This function generates a random number using Marsaglia's Random Number Generator

    Parameters
    ----------
    base : int, optional
        The base
    lag_r : int, optional
        The lag r
    lag_s : int, optional
        The lag s
    carry : int, optional
        The carry
    seed_tuple : tuple, optional
        The seed tuple

    Returns
    -------
    float
        The generated random number
    """
    global marsaglia_vars  # Use the global dictionary marsagliaVars
    if (  # Check if the global dictionary marsagliaVars is initialized
        marsaglia_vars["base"] == None
        or marsaglia_vars["lag_r"] == None
        or marsaglia_vars["lag_s"] == None
        or marsaglia_vars["carry"] == None
        or marsaglia_vars["args"] == None
    ):
        if (  # Check if the parameters are None
            base == None
            or lag_r == None
            or lag_s == None
            or carry == None
            or seed_tuple == None
        ):
            marsaglia_init(
                2**31 - 1, 19, 7, 1, (1, 1)
            )  # Initialize the global dictionary marsagliaVars with default values
            print(
                f'Marsaglia Random Number Generator Initialized with default values\n\tbase={marsaglia_vars["base"]}\n\tlag_r={marsaglia_vars["lag_r"]}\n\tlag_s={marsaglia_vars["lag_s"]}\n\tcarry={marsaglia_vars["carry"]}\n\tseed_tuple={marsaglia_vars["args"]}'
            )
        else:  # Initialize the global dictionary marsagliaVars with the parameters passed
            marsaglia_init(base, lag_r, lag_s, carry, seed_tuple)
    new_random_number = (
        marsaglia_vars["args"][0]
        - marsaglia_vars["args"][marsaglia_vars["lag_r"] - marsaglia_vars["lag_s"]]
        - marsaglia_vars["carry"]
    )  # f(x_1...x_r,c) =    | (x_2,...,x_r, x_1-x_{r-s} - c , 0)      if x_1-x_{r-s} - c >= 0
    #                     | (x_2,...,x_r, x_1-x_{r-s} - c + b, 1)   if x_1-x_{r-s} - c < 0
    if new_random_number < 0:  # Check if x_1-x_{r-s} - c < 0
        new_random_number += marsaglia_vars["base"]  # Add b to x_1-x_{r-s} - c
        marsaglia_vars["carry"] = 1  # Set carry to 1
    else:
        marsaglia_vars["carry"] = 0  # Set carry to 0

    marsaglia_vars["args"] = marsaglia_vars["args"][1:] + [
        new_random_number
    ]  # Set the values of x_1...x_r to x_2...x_r, x_1-x_{r-s} - c
    return new_random_number / marsaglia_vars["base"]  # Return the random number


# Mersenne Twister Random Number Generator
mt_vars = {
    "N": None,  # N
    "M": None,  # M
    "MATRIX_A": None,  # MATRIX_A
    "UPPER_MASK": None,  # UPPER_MASK
    "LOWER_MASK": None,  # LOWER_MASK
    "TEMPERING_MASK_B": None,  # TEMPERING_MASK_B
    "TEMPERING_MASK_C": None,  # TEMPERING_MASK_C
    "mt": None,  # mt
    "mti": None,  # mti
}


def clear_mt_vars():
    """
    This function clears the global dictionary mtVars

    Returns
    -------
    None
    """
    global mt_vars
    mt_vars = {
        "N": None,  # N
        "M": None,  # M
        "MATRIX_A": None,  # MATRIX_A
        "UPPER_MASK": None,  # UPPER_MASK
        "LOWER_MASK": None,  # LOWER_MASK
        "TEMPERING_MASK_B": None,  # TEMPERING_MASK_B
        "TEMPERING_MASK_C": None,  # TEMPERING_MASK_C
        "mt": None,  # mt
        "mti": None,  # mti
    }


def sgenrand(seed):
    """
    This function initializes the global dictionary mtVars

    Parameters
    ----------
    seed : int
        The seed

    Returns
    -------
    None
    """
    global mt_vars
    mt_vars = {
        "N": 624,  # N
        "M": 397,  # M
        "MATRIX_A": 0x9908B0DF,  # MATRIX_A
        "UPPER_MASK": 0x80000000,  # UPPER_MASK
        "LOWER_MASK": 0x7FFFFFFF,  # LOWER_MASK
        "TEMPERING_MASK_B": 0x9D2C5680,  # TEMPERING_MASK_B
        "TEMPERING_MASK_C": 0xEFC60000,  # TEMPERING_MASK_C
        "mt": [0] * 624,  # mt
        "mti": 624 + 1,  # mti
        "TEMPERING_SHIFT_U": lambda y: y >> 11,  # TEMPERING_SHIFT_U(y)
        "TEMPERING_SHIFT_S": lambda y: y << 7,  # TEMPERING_SHIFT_S(y)
        "TEMPERING_SHIFT_T": lambda y: y << 15,  # TEMPERING_SHIFT_T(y)
        "TEMPERING_SHIFT_L": lambda y: y >> 18,  # TEMPERING_SHIFT_L(y)
    }

    mt_vars["mt"][0] = seed & 0xFFFFFFFF
    mt_vars["mti"] = 1
    while mt_vars["mti"] < mt_vars["N"]:
        mt_vars["mt"][mt_vars["mti"]] = (
            69069 * mt_vars["mt"][mt_vars["mti"] - 1]
        ) & 0xFFFFFFFF
        mt_vars["mti"] += 1


def genrand(seed: int = None):
    global mt_vars

    # Check if the global dictionary mtVars is initialized
    if (
        mt_vars["N"] is None
        or mt_vars["M"] is None
        or mt_vars["MATRIX_A"] is None
        or mt_vars["UPPER_MASK"] is None
        or mt_vars["LOWER_MASK"] is None
        or mt_vars["TEMPERING_MASK_B"] is None
        or mt_vars["TEMPERING_MASK_C"] is None
        or mt_vars["mt"] is None
        or mt_vars["mti"] is None
    ):
        if seed is None:
            seed = 4357
        if type(seed) is not int:
            raise ValueError("The seed must be an integer")
        sgenrand(seed)
        print("Initialized the global dictionary mtVars with seed " + str(seed))

    mag01 = [0x0, mt_vars["MATRIX_A"]]

    # Generate N words at one time
    if mt_vars["mti"] >= mt_vars["N"]:
        kk = 0
        y = None

        while kk < mt_vars["N"] - mt_vars["M"]:
            y = (mt_vars["mt"][kk] & mt_vars["UPPER_MASK"]) | (
                mt_vars["mt"][kk + 1] & mt_vars["LOWER_MASK"]
            )  # y = (mt[kk] AND UPPER_MASK) OR (mt[kk + 1] AND LOWER_MASK)
            mt_vars["mt"][kk] = (
                mt_vars["mt"][kk + mt_vars["M"]] ^ (y >> 1) ^ mag01[y & 0x1]
            )  # mt[kk] = mt[kk + M] XOR (y >> 1) XOR mag01[y AND 0x1]
            kk += 1

        while kk < mt_vars["N"] - 1:
            y = (mt_vars["mt"][kk] & mt_vars["UPPER_MASK"]) | (
                mt_vars["mt"][kk + 1] & mt_vars["LOWER_MASK"]
            )  # y = (mt[kk] AND UPPER_MASK) OR (mt[kk + 1] AND LOWER_MASK)
            mt_vars["mt"][kk] = (
                mt_vars["mt"][kk + (mt_vars["M"] - mt_vars["N"])]
                ^ (y >> 1)
                ^ mag01[y & 0x1]
            )  # mt[kk] = mt[kk + (M - N)] XOR (y >> 1) AND mag01[y & 0x1]
            kk += 1

        y = (mt_vars["mt"][mt_vars["N"] - 1] & mt_vars["UPPER_MASK"]) | (
            mt_vars["mt"][0] & mt_vars["LOWER_MASK"]
        )  # y = (mt[N - 1] AND UPPER_MASK) OR (mt[0] AND LOWER_MASK)
        mt_vars["mt"][mt_vars["N"] - 1] = (
            mt_vars["mt"][mt_vars["M"] - 1] ^ (y >> 1) ^ mag01[y & 0x1]
        )  # mt[N - 1] = mt[M - 1] XOR (y >> 1) XOR mag01[y & 0x1]

        mt_vars["mti"] = 0

    y = mt_vars["mt"][mt_vars["mti"]]  # y = mt[mti++]
    mt_vars["mti"] += 1

    # Tempering
    y ^= mt_vars["TEMPERING_SHIFT_U"](y)
    y ^= mt_vars["TEMPERING_SHIFT_S"](y) & mt_vars["TEMPERING_MASK_B"]
    y ^= mt_vars["TEMPERING_SHIFT_T"](y) & mt_vars["TEMPERING_MASK_C"]
    y ^= mt_vars["TEMPERING_SHIFT_L"](y)

    return y / 0xFFFFFFFF
