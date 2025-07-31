# Uses zxcvbn library to rate password and give suggestions

from zxcvbn import zxcvbn


def pwd_score(pwd):
    if pwd:
        results = zxcvbn(pwd)
        return round(results["guesses_log10"], 2)


def pwd_strength(pwd):
    if pwd:
        score = pwd_score(pwd)
        if score < 4:
            return "Weak"
        if score < 9:
            return "Moderate"
        else:
            return "Strong"


def pwd_feedback(pwd):
    if pwd:
        results = zxcvbn(pwd)
        feedback = results["feedback"]
        output = ""
        if feedback["warning"]:
            output += f"Warning: {feedback["warning"]}\n"
        if feedback["suggestions"]:
            output += f"Suggestions: \n"
            for suggestion in feedback["suggestions"]:
                output += f"- {suggestion}\n"
        return output

