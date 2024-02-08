import random
import datetime
from qiskit import Aer, execute
from qiskit.circuit import QuantumCircuit
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from time import time
# from qiskit.providers.aer import Aer

# 设置为使用GPU后端
# backend = Aer.get_backend('aer_simulator_gpu')

# Existing functions: convert_to_lunar_date() and generate_draws_based_on_date_and_stars() remain unchanged
# 假设规则来模拟农历日期和星相的影响
def generate_draws_based_on_date_and_stars():
    # 当前日期和时间
    current_date = datetime.datetime.now()
    current_hour = current_date.hour

    # 假设基于农历和星相的调整因子（这里使用示例值）
    # lunar_adjustment = current_date.day  # 假设农历日期影响
    # 基于农历日期的调整因子
    lunar_adjustment = lunar_lucky_day
    star_adjustment = 25 / 24  # 假设星相影响
    print("lunar_adjustment:",int(lunar_adjustment * 1000000))
    print("star_adjustment:", int(star_adjustment * 1000000))
    # 调整随机数的生成范围
    lower_bound = 175000000 + int(lunar_adjustment * 1000000)
    upper_bound = 210000000 - int(star_adjustment * 1000000)

    # 生成随机数
    num_draws = random.randint(lower_bound, upper_bound)
    return num_draws

def convert_to_lunar_date():
    # 邵子神数取卦方法
    lunar_month = 12  # 农历月份
    lunar_day = 25  # 农历日期
    lunar_year = 2023  # 农历年份
    total = lunar_year + lunar_month + lunar_day

    # 将总和转换为卦象（每个卦由6位组成，每位为0或1）
    # 这里使用取余的方式模拟掷币过程
    gua = [(total >> i) & 1 for i in range(6)]

    # 将卦象转换为一个数字
    lunar_lucky_day = sum(value * (2 ** index) for index, value in enumerate(gua))
    return lunar_lucky_day
# Function to generate a single lottery draw
def generate_single_lottery_draw(num_draws_lucky):
    qc = QuantumCircuit(5)
    qc.h(range(5))
    qc.measure_all()
    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=1)
    result = job.result()
    counts = result.get_counts()
    measurement = list(counts.keys())[0]
    number = int(measurement, 2)
    reds = sorted(random.sample(range(1, 34), 6))
    blue = number % 16 + 1
    return reds, blue


# Parallel computation of lottery draws with progress bar
def generate_lottery_numbers_qmc_parallel(num_draws):
    futures = []
    results = []
    start_time = time()
    with ThreadPoolExecutor() as executor:
        for _ in tqdm(range(num_draws), desc="Scheduling draws"):
            future = executor.submit(generate_single_lottery_draw, 0)
            futures.append(future)
        results = [future.result() for future in tqdm(as_completed(futures), total=num_draws, desc="Calculating draws")]
        end_time = time()  # End timing
        # total_time = end_time - start_time  # Calculate total time taken
        # print(f"Total time taken: {total_time:.2f} seconds")

        for future in tqdm(as_completed(futures), total=num_draws, desc="Calculating draws"):
            results.append(future.result())
    total_time = end_time - start_time
    print(f"Total time taken: {total_time:.2f} seconds")
    return results
#
lunar_lucky_day = convert_to_lunar_date()
num_draws_lucky = generate_draws_based_on_date_and_stars()
print("预测销售总数：", num_draws_lucky)
lottery_draws = generate_lottery_numbers_qmc_parallel(1000)

blue_frequency = Counter([blue for _, blue in lottery_draws])
red_frequency = Counter([red for reds, _ in lottery_draws for red in reds])

print("\n蓝球号码出现频率（从低到高）:")
for num, freq in sorted(blue_frequency.items(), key=lambda x: x[1]):
    print(f"号码 {num}: 出现次数 {freq}")
print("红球号码出现频率（从低到高）:")
for num, freq in sorted(red_frequency.items(), key=lambda x: x[1]):
    print(f"号码 {num}: 出现次数 {freq}")

least_frequent_blue = sorted(blue_frequency, key=blue_frequency.get)[:1]
least_frequent_reds = sorted(red_frequency, key=red_frequency.get)[:6]
file_path = '61.txt'
with open(file_path, 'w') as file:
    file.write("6: " + str(least_frequent_reds) + "\n")
    file.write("1: " + str(least_frequent_blue))
