from pymvola.models import Transaction


def test_to_schema():
    # Create a Transaction instance
    amount = 1000
    description_text = "Payement Marchant"
    creditor = "0343500004"
    debitor = "0343500003"
    transaction = Transaction(amount, description_text, creditor, debitor)

    # Define the expected dictionary
    expected_schema = {
        "amount": "1000",
        "currency": "Ar",
        "descriptionText": "Payement Marchant",
        "requestingOrganisationTransactionReference": ...,
        "requestDate": ...,
        "originalTransactionReference": "",
        "debitParty": [{"key": "msisdn", "value": "0343500003"}],
        "creditParty": [{"key": "msisdn", "value": "0343500004"}],
        "metadata": [
            {"key": "partnerName", "value": "TestBlueline"},
            {"key": "fc", "value": "USD"},
            {"key": "amountFc", "value": "1"},
        ],
    }

    transaction_schema = transaction.to_schema("TestBlueline")

    # assertions for the presence of dynamic keys
    assert "requestingOrganisationTransactionReference" in transaction.to_schema(
        "TestBlueline"
    )
    assert "requestDate" in transaction.to_schema("TestBlueline")

    # remove dynamic keys
    del (
        transaction_schema["requestDate"],
        transaction_schema["requestingOrganisationTransactionReference"],
    )
    del (
        expected_schema["requestDate"],
        expected_schema["requestingOrganisationTransactionReference"],
    )

    # Call the to_schema method and compare with the expected dictionary
    assert transaction_schema == expected_schema
