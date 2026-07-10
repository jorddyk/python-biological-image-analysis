"""Day 1 proof-of-work for Python biological image-analysis training.

Demonstrates variables, lists, loops, functions, enumeration, and formatted output.
No unpublished research data are used.
"""


def summarize_course_day(day_number, topics):
    """Return a readable summary of topics logged for one course day."""
    topic_count = len(topics)
    topic_text = ", ".join(topics)
    return f"Day {day_number}: {topic_count} topics logged — {topic_text}"


def main():
    """Print the Day 1 course progress summary and topic checklist."""
    day_1_topics = [
        "Python environment setup",
        "terminal commands",
        "object types",
        "loops",
        "functions",
    ]

    print("Python for Biological Image Analysis")
    print(summarize_course_day(1, day_1_topics))

    print("\nTopic checklist:")
    for index, topic in enumerate(day_1_topics, start=1):
        print(f"{index}. {topic}")


if __name__ == "__main__":
    main()
