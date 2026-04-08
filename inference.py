import asyncio
from env import Action
from app import env, generate_rule_based_tests


def log_start():
    print("[START] task=testgen env=testgen_env model=default")


def log_step(step, action, reward, done, error):
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error or 'null'}")


def log_end(success, steps, score, rewards):
    joined = ",".join(f"{value:.2f}" for value in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={joined}")


async def main():
    rewards = []
    log_start()

    observation = env.reset()
    test_code = generate_rule_based_tests(observation.function_code)

    result = env.step(Action(test_code=test_code))
    rewards.append(result.reward)
    log_step(1, "test_generation", result.reward, result.done, result.info)

    score = sum(rewards) / len(rewards)
    log_end(True, len(rewards), score, rewards)


if __name__ == "__main__":
    asyncio.run(main())
