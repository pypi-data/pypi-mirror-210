import typing
import urllib.parse

import aiohttp

from .platform import Platform

_english_pronouns: dict[str, list[str]] = {
    "unspecified": [],
    "he": ["he", "him"],
    "she": ["she", "her"],
    "they": ["they", "them"],
    "any": ["any"],
    "other": ["other"],
    "ask": ["ask"],
    "avoid": ["use name"],
}


async def lookup(platform: Platform, identifiers: typing.Union[str, int, list[str], list[int]], pronouns=None) -> \
        typing.Union[dict[str, list[str]], dict[int, list[str]]]:
    """
    Sends a request to the PronounDB API to get the pronouns of one or multiple users.
    If more than 50 identifiers are passed, the wrapper will automatically split the request into multiple requests.

    :param platform: One of the supported platforms (see the Platform enum)
    :param identifiers: Account IDs on the platform
    :param pronouns: An optional parameter that allows specifying the desired language for the returned pronouns.
                     By default, English pronouns are used (see _english_pronouns).
                     You can use this argument to retrieve pronouns in other languages by providing
                     a dictionary with the corresponding pronouns for the desired language.
    :return: The pronouns of the users as a list of all the pronouns the users use
    """

    if pronouns is None:
        pronouns = _english_pronouns

    if not isinstance(identifiers, list):
        identifiers = [identifiers]

    def get_pronouns_set(pronoun: str) -> list[str]:
        if not pronoun in pronouns:
            raise ValueError(f'{pronoun} not in pronouns parameter.')

        return pronouns[pronoun]

    all_results = {}

    for i in range(0, len(identifiers), 50):
        batch: typing.Union[list[str], list[int]] = identifiers[i:i + 50]

        async with aiohttp.ClientSession() as session:
            async with session.get("https://pronoundb.org/api/v2/lookup?platform={0}&ids={1}".format(
                    platform.value,
                    urllib.parse.quote_plus(",".join(map(str, batch)))
            )) as resp:
                data = await resp.json()

                if "error" in data:
                    raise ValueError(f'{data["error"]}: {data["message"]}')

                for identifier in batch:
                    if len(data) == 0:
                        all_results[identifier] = get_pronouns_set("unspecified")
                        continue

                    user_data = data[str(identifier)]
                    english_set = user_data["sets"]["en"]

                    if len(english_set) == 1:
                        all_results[identifier] = get_pronouns_set(english_set[0])
                    else:
                        all_results[identifier] = [
                            get_pronouns_set(english_set[0])[0],
                            get_pronouns_set(english_set[1])[0]
                        ]

    return all_results
