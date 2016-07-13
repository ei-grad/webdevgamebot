"""Вы начинающий директор веб-студии!

Нанимайте дизайнеров, разработчиков и админов, берите заказы, развивайтесь!

Вы получаете средства за разработку и поддержку, платите зарплаты работникам и
HR-агенству за найм новых сотрудников.
"""

import asyncio
import random

from telegram_game import BaseGame


class Outcome:

    def __init__(self, *outcome_list):
        self.outcome = []
        for weight, outcome in outcome_list:
            self.outcome.extend([outcome] * weight)

    def choice(self):
        return random.choice(self.outcome)


class O:
    def __init__(self, message, **effect):
        self.message = message
        self.effect = effect


EVENTS = [
    ("HR-ы говорят что нашли разработчика, нанимаем?", {
        "Лишние руки всегда пригодятся, а мозги - тем более!": Outcome(
            (2, O('Разраб шарит! Но теперь нужно выплатить HR-ам премию.',
                  dev=1, balance=-100)),
            (1, O('Он оказался долбанутым студентом и запорол проект!',
                  balance=-100, active=-1)),
        ),
        "Их и так слишком много.": Outcome(
            (1, O('Вы упустили выгодный заказ потому что не кому было им заняться!',
                  )),
            (1, O('По одному из проектов были провалены сроки и '
                  'заказчик отказался от ваших услуг!',
                  active=-1)),
            (1, O('Один из разработчиков услышал и обиделся.',
                  devs=-1)),
        ),
        "Вернуться к вопросу в следующем месяце...": Outcome(
            (1, O('Время идет, зима близко...')),
        ),
    }),
]


class Game(BaseGame):

    async def start(self):

        await self.recv()

        await self.send(__doc__)

        state = {
            'design': 1,
            'dev': 1,
            'admin': 1,
            'active': 1,
            'support': 0,
            'balance': 1000,
        }

        while True:

            event, variants = random.choice(EVENTS)

            msg = [
                "Штат:",
                "{design} дизайнеров",
                "{dev} разработчиков",
                "{admin} админов",
                "Проекты:",
                "{active} в разработке",
                "{support} на поддержке",
                "На счету: {balance}",
                event,
            ]

            await self.send('\n'.join(msg).format(**state), reply_markup={
                'keyboard': [[i] for i in variants],
                'one_time_keyboard': True,
            })

            answer = await self.recv()

            await asyncio.sleep(1)

            outcome = variants[answer['message']['text']].choice()

            for key, value in outcome.effect.items():
                state[key] += value

            await self.send(outcome.message)

            await asyncio.sleep(1)
