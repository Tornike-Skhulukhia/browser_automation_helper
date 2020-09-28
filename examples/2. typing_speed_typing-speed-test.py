from browser_automation_helper.br_helper import BrowserHelper
import time

br = BrowserHelper(
                    browser="firefox", driver_path="/home/tornike/bin/geckodriver",
                    options={'hide_images': 1, "visibility": 1},
                    )

# navigate
br.get('https://typing-speed-test.aoeu.eu/')

# activate typing mode
br.find('type the words here').click()


document_body = br.css1('body')


while True:
    active_word = br.css1('span.currentword').text
    
    document_body.send_keys(active_word + " ")

    print(f"Typed word: {active_word}")
    # time.sleep(0.1)

    print("-" * 100)
