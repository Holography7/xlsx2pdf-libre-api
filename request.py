import requests


def get_pdf(filepath_in: str, filepath_out: str, url: str) -> None:
    # read file
    with open(filepath_in, 'rb') as xlsx:
        data = xlsx.read()

    # send bytes and response pdf
    res = requests.post(
        url=url,
        data=data,
        headers={'Content-Type': 'application/octet-stream'},
    )

    # handling not 200 status response
    res.raise_for_status()

    # write pdf to disk
    with open(filepath_out, 'wb') as pdf:
        pdf.write(res.content)


if __name__ == '__main__':
    get_pdf(
        'example.xlsx',
        'example.pdf',
        'http://0.0.0.0:8070/convert_to_pdf',
    )
