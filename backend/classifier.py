# TEMP classifier (until mbert model trains)

def predict_category(text: str):

    text = text.lower()

    if "network" in text or "internet" in text:
        return "network_issue"

    elif "bill" in text or "payment" in text:
        return "billing_issue"

    elif "sim" in text:
        return "sim_issue"

    elif "recharge" in text:
        return "recharge_issue"

    else:
        return "general_query"