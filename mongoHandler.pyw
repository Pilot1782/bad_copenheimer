import subprocess
import time

bot_download = "https://raw.githubusercontent.com/Pilot1782/bad_copenheimer/dev-builds/mongoBot.pyw"

def download_bot():
    subprocess.call(["curl", bot_download, "-o", "mongoBot.pyw"])

def run_bot():
    # after 6 hours, restart the bot
    botProc = subprocess.Popen(['python3', 'mongoBot.pyw'])
    time.sleep(21600)
    botProc.kill()

    download_bot()


def main():
    while True:
        try:
            run_bot()
        except:
            download_bot()
            run_bot()


if __name__ == '__main__':
    main()