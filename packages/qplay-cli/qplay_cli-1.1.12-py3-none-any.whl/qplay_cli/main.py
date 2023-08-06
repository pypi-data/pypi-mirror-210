import click
from qplay_cli.dataset.commands import dataset
from qplay_cli.user.commands import user
from qplay_cli.machine.commands import machine
from qplay_cli.broker.commands import broker
from qplay_cli.market.commands import market
from qplay_cli.strategy.commands import strategy

@click.group()
def quantplay():
    pass

quantplay.add_command(dataset)
quantplay.add_command(user)
quantplay.add_command(machine)
quantplay.add_command(broker)
quantplay.add_command(market)
quantplay.add_command(strategy)
    
if __name__ == '__main__':
    quantplay()