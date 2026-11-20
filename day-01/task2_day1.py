QUALIFY_SECONDS = 25 * 60  


def time_to_seconds(text):
    """Convert 'mm:ss' to seconds. Return -1 if invalid."""
    parts = text.split(":")
    if len(parts) != 2:
        return -1

    minutes_text = parts[0].strip()
    seconds_text = parts[1].strip()

    if not minutes_text.isdigit() or not seconds_text.isdigit():
        return -1

    minutes = int(minutes_text)
    seconds = int(seconds_text)

    if seconds > 59:
        return -1

    return minutes * 60 + seconds


def seconds_to_time(total):
    minutes = total // 60
    seconds = total % 60
    return str(minutes).zfill(2) + ":" + str(seconds).zfill(2)


def main():
    qualifiers = 0
    entries = 0          
    best_time = -1
    winners = ""

    print("Enter athlete name and time")

    while True:
        name = input("Name of athlete: ").strip()
        if name.lower() == "x":
            break

        time_text = input("Time: ").strip()
        if time_text.lower() == "x":
            break

        seconds = time_to_seconds(time_text)
        if seconds == -1:
            print("  Invalid time - ignored.")
            continue

        entries = entries + 1

        if seconds <= QUALIFY_SECONDS:
            qualifiers = qualifiers + 1

        if best_time == -1 or seconds < best_time:
            best_time = seconds
            winners = name
        elif seconds == best_time:
            winners = winners + " and " + name

    print()
    if entries == 0:
        print("No valid entries.")
    else:
        print("Winner: " + winners + " (" + seconds_to_time(best_time) + ")")
        print("Qualified: " + str(qualifiers) + " of " + str(entries))


main()

