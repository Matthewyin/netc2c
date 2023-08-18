# def convert_seconds_to_time(seconds):
#     # 计算年、月、日、时、分、秒
#     years = seconds // (365 * 24 * 60 * 60)
#     remaining_seconds = seconds % (365 * 24 * 60 * 60)
#
#     months = remaining_seconds // (30 * 24 * 60 * 60)
#     remaining_seconds = remaining_seconds % (30 * 24 * 60 * 60)
#
#     days = remaining_seconds // (24 * 60 * 60)
#     remaining_seconds = remaining_seconds % (24 * 60 * 60)
#
#     hours = remaining_seconds // (60 * 60)
#     remaining_seconds = remaining_seconds % (60 * 60)
#
#     minutes = remaining_seconds // 60
#     seconds = remaining_seconds % 60
#
#     return years, months, days, hours, minutes, seconds