def record_time(filename):
    # 현재 시간
    current_time = datetime.datetime.now()

    # CSV 파일에 현재 시간을 기록
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([current_time])
