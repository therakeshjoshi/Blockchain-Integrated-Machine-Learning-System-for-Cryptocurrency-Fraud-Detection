{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyODercv1ia5MT1+W8D2ef+k"
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "code",
      "execution_count": 1,
      "metadata": {
        "id": "UdO_NYFjXX_t",
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "outputId": "04361ad7-bc90-4754-8497-902a94caaf7e"
      },
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Input Data: {'TimeStamp': 1529873859, 'Value': 0.5, 'minValReceived': 0.01, 'totalTransactions': 12}\n",
            "Generated SHA-256 Hash: 0x9386e2a5cca3483e991b97bb9c7176533b08bee6d5ea666798c7eeb6b663207c\n"
          ]
        }
      ],
      "source": [
        "import hashlib\n",
        "import json\n",
        "\n",
        "def generate_hash(transaction_data):\n",
        "\n",
        "\n",
        "    clean_data = {}\n",
        "    for key, value in transaction_data.items():\n",
        "        if hasattr(value, 'item'):\n",
        "            value = value.item()\n",
        "        clean_data[key] = value\n",
        "\n",
        "    transaction_string = json.dumps(clean_data, sort_keys=True)\n",
        "\n",
        "\n",
        "    encoded_transaction = transaction_string.encode('utf-8')\n",
        "    hash_object = hashlib.sha256(encoded_transaction)\n",
        "    hex_dig = hash_object.hexdigest()\n",
        "\n",
        "    return \"0x\" + hex_dig\n",
        "\n",
        "if __name__ == \"__main__\":\n",
        "\n",
        "    sample_tx = {\n",
        "        'TimeStamp': 1529873859,\n",
        "        'Value': 0.5,\n",
        "        'minValReceived': 0.01,\n",
        "        'totalTransactions': 12\n",
        "    }\n",
        "\n",
        "    fingerprint = generate_hash(sample_tx)\n",
        "    print(f\"Input Data: {sample_tx}\")\n",
        "    print(f\"Generated SHA-256 Hash: {fingerprint}\")"
      ]
    },
    {
      "cell_type": "code",
      "source": [],
      "metadata": {
        "id": "dAC2JVn-Xvsc"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}