import matplotlib.pyplot as plt
import io, base64


def generate_registration_plot(data):
    """

    Generates a bar plot showing user registrations per week.

    Parameters:
        data (list of tuples): Each tuple contains a date (str) and the total number of registrations.

    Returns:
        str: Base64-encoded string of the PNG image.

    """
    # Extract dates (week start) and registration counts from input data
    dates = [item[0] for item in data]
    counts = [item[1] for item in data]

    # Create the figure and bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(dates, counts, color='#0d94b0')

    # Set labels and title
    plt.xlabel('Week (Monday)')
    plt.ylabel('Registered Users')
    plt.title('Registrations per Week')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save plot to a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Convert buffer content to base64 encoding
    plot_data = buf.getvalue()
    plot_url = base64.b64encode(plot_data).decode('utf8')

    # Close the plot to free memory
    plt.close()

    return plot_url
