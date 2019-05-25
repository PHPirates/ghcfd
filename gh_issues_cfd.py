import datetime
import pickle
import sys

import numpy
from github import Github
from matplotlib import pyplot

if __name__ == '__main__':
    """ 
    Usage: give username and password as parameters. 
    Delete the issues_dump file to retrieve new statistics.
    """

    USERNAME = sys.argv[1]
    PASSWORD = sys.argv[2]
    GITHUB_REPO = 'Ruben-Sten/TeXiFy-IDEA'
    PLOT_TITLE = f'Number of open {GITHUB_REPO} issues and pull requests'

    # Issues per this time span, in days
    time_span = 1

    g = Github(USERNAME, PASSWORD)
    repo = g.get_repo(GITHUB_REPO)

    weeks_arr = []
    issues_dump = None
    try:
        issues_dump = pickle.load(open("issues_dump", "rb"))
    except Exception:
        issues_dump = None

    # Retrieve the issues
    if issues_dump is None:
        issues_arr_dump = []
        issues = repo.get_issues("*", "closed")
        for issue in issues:
            issues_arr_dump.append(issue)
        issues = repo.get_issues("none", "closed")
        for issue in issues:
            issues_arr_dump.append(issue)
        issues = repo.get_issues("none", "open")
        for issue in issues:
            issues_arr_dump.append(issue)
        issues = repo.get_issues("*", "open")
        for issue in issues:
            issues_arr_dump.append(issue)
        pickle.dump(issues_arr_dump, open("issues_dump", "wb"))
    issues_dump = pickle.load(open("issues_dump", "rb"))
    issues_dump.reverse()

    # Find the first and last issue
    max_issue_num = 0
    max_issue = None
    min_issue = None
    for issue in issues_dump:
        if issue.number > max_issue_num:
            max_issue_num = issue.number
            max_issue = issue
        if issue.number == 1:
            min_issue = issue

    proj_start_date = min_issue.created_at
    proj_end_date = datetime.datetime.now()

    # Find the week of the first and last issue
    proj_start_week_date = proj_start_date
    if proj_start_date.weekday() != 0:
        proj_start_week_date -= \
            datetime.timedelta(days=proj_start_date.weekday())

    current_date = datetime.datetime.now()
    proj_end_week_date = current_date
    if proj_end_date.weekday() != 4:
        proj_end_week_date += \
            datetime.timedelta(days=4 - proj_end_date.weekday())

    last_week_start_date = proj_end_week_date - datetime.timedelta(days=4)

    date_inc = proj_start_week_date
    current_week_start_date = None

    # Start with the first day of the first 'week', then increase by time_span
    # days. Note that a 'week' lasts time_span days, and may not be a week.
    while date_inc <= last_week_start_date:
        if date_inc.weekday() == 0:
            current_week_start_date = date_inc

        current_week_end_date = current_week_start_date + datetime.timedelta(
            days=time_span)

        # Number of open issues in a certain week
        nr_open_issues = 0
        nr_closed_issues = 0

        counter = 0

        while counter < len(issues_dump):

            issue = issues_dump[counter]
            if (issue.created_at <= current_week_start_date) and \
                    (
                            issue.state != 'closed'
                            or issue.closed_at >= current_week_start_date
                    ):
                nr_open_issues += 1

            counter += 1

        weeks_arr.append([date_inc,
                          current_week_end_date.strftime('%Y-%m-%d'),
                          nr_open_issues, nr_closed_issues])
        date_inc += datetime.timedelta(days=time_span)

    arr_opened = [item[2] for item in weeks_arr]
    # arr_closed = [item[3] for item in weeks_arr]
    # arr_stack = numpy.row_stack((arr_closed, arr_opened))

    # weeks = numpy.arange(0, len(arr_opened), 1)
    x_values = [item[0] for item in weeks_arr]
    y_values = arr_opened

    print("Last data:")
    print(x_values[-1:])
    print(y_values[-1:])

    fig, ax = pyplot.subplots()
    pyplot.xticks(rotation=70)
    ax.plot(x_values, y_values)
    plot_vert_height = max(y_values)

    pyplot.title(PLOT_TITLE)
    ax.set_ylabel('Issues + pull requests')
    # ax.set_xlim(0, len(weeks_arr) - 1)
    ax.set_ylim(0, plot_vert_height + plot_vert_height * 0.1)
    # ax.legend(['Closed', 'Opened'])
    plot_file_name = 'gh_issues_plot_' + str(
        current_date.strftime('%Y-%m-%d')) + '.png'
    plot_file = pyplot.savefig(plot_file_name)
    pyplot.show()
