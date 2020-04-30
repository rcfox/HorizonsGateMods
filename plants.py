import networkx
from networkx.drawing.nx_pydot import write_dot as _write_dot
from boatlib.data import ItemType, ItemReaction, Collection, collect_records

def define_turnip():
    G = networkx.MultiDiGraph()
    G.add_edge('turnip', 'turnip_seeds', element='smash', spawnItem=['turnip_seeds', 'turnip_seeds'])
    G.add_edge('turnip_seeds', 'turnip_seeds_watered', element='water')
    G.add_edge('turnip_seeds_watered', 'turnip_sprout', element='newDay', count=3,
               description='It will sprout in {days} day{s}.')

    G.add_edge('turnip_sprout', 'turnip_sprout_watered', element='water')
    G.add_edge('turnip_sprout_watered', 'turnip_mature', element='newDay', count=7,
               description='It will mature in {days} day{s}.')

    G.add_edge('turnip_mature', 'turnip', element='use')

    G.nodes['turnip']['properties'] = dict(
        name='Turnip',
        itemCategory='plant',
        texture='rcfox_farming_crops',
        sprite=0,
    )
    G.nodes['turnip_seeds']['properties'] = dict(
        name='Turnip Seeds',
        itemCategory='plant',
        texture='rcfox_farming_crops',
        sprite=5,
    )
    G.nodes['turnip_seeds_watered']['properties'] = dict(
        name='Turnip Seeds (Watered)',
        itemCategory='hide',
        cloneFrom='turnip_seeds',
        special=['dontCloneReactions', 'cannotBePickedUp']
    )
    G.nodes['turnip_sprout']['properties'] = dict(
        name='Turnip Sprout',
        itemCategory='plant',
        texture='rcfox_farming_crops',
        sprite=2,
        special='cannotBePickedUp'
    )
    G.nodes['turnip_sprout_watered']['properties'] = dict(
        name='Turnip Sprout (watered)',
        itemCategory='hide',
        cloneFrom='turnip_sprout',
        special=['dontCloneReactions', 'cannotBePickedUp']
    )
    G.nodes['turnip_mature']['properties'] = dict(
        name='Turnip (mature)',
        itemCategory='plant',
        texture='rcfox_farming_crops',
        sprite=1,
        special='cannotBePickedUp'
    )

    return graph_to_plants(expand_graph(G))

def define_aldleaf_plant():
    G = networkx.MultiDiGraph()
    G.add_edge('aldleaf', 'aldleafSeeds', element='smash')
    G.add_edge('aldleafSeeds', 'aldleafSeeds_watered', element='water')
    G.add_edge('aldleafSeeds_watered', 'aldleafSprout', element='newDay')
    G.add_edge('aldleafSeeds', 'aldleafSprout', element='growth')
    G.add_edge('aldleafSprout', 'aldleafPlant_deadend', element='growth')
    G.add_edge('aldleafSprout', 'aldleafPlant', element='newDay', count=3,
               description='It will develop leaves in {days} day{s}.',
               element_targets={'growth': 'aldleafPlant_deadend'})

    G.add_edge('aldleafPlant', 'aldleafPlant_watered', element='water')
    G.add_edge('aldleafPlant_watered', 'aldleafBush', element='newDay', count=7,
               description='It will mature in {days} day{s}.',
               element_targets={'slash': 'aldleaf'})

    G.add_edge('aldleafBush', 'aldleafBush_watered', element='water')
    G.add_edge('aldleafBush_watered', 'aldleafBush', element='newDay', count=7,
               description='It will produce fruit in {days} day{s}.',
               spawnItem='sleep_fruit')

    G.add_edge('aldleafPlant', 'aldleafPlant_wither', element='newDay', count=7,
               element_targets={'water': 'aldleafPlant_watered', 'growth': 'aldleafPlant'})
    G.add_edge('aldleafBush', 'aldleafBush_wither', element='newDay', count=7,
               element_targets={'water': 'aldleafBush_watered', 'growth': 'aldleafBush'})

    G.add_edge('aldleafPlant_wither', 'aldleafPlant', element='growth')
    G.add_edge('aldleafBush_wither', 'aldleafBush', element='growth')

    G.nodes['aldleaf']['properties'] = dict(
        cloneFrom='aldleaf'
    )
    G.nodes['aldleafSeeds']['properties'] = dict(
        name='Aldleaf Seeds',
        itemCategory='plant',
        sprite=483,
        description='Seeds!'
    )
    G.nodes['aldleafSeeds_watered']['properties'] = dict(
        name='Aldleaf Seeds (Watered)',
        itemCategory='hide',
        cloneFrom='aldleafSeeds',
        special=['dontCloneReactions', 'cannotBePickedUp']
    )
    G.nodes['aldleafSprout']['properties'] = dict(
        name='Aldleaf Sprout',
        itemCategory='plant',
        sprite=556,
        description='It will develop leaves in 3 day.',
        special='cannotBePickedUp'
    )
    G.nodes['aldleafPlant']['properties'] = dict(
        cloneFrom='aldleafPlant',
        special='dontCloneReactions',
        description='It will mature in 7 days if watered.',
    )
    G.nodes['aldleafPlant_deadend']['properties'] = dict(
        cloneFrom='aldleafPlant',
        special='dontCloneReactions'
    )
    G.nodes['aldleafPlant_wither']['properties'] = dict(
        cloneFrom='aldleafPlant_wither',
        special='dontCloneReactions'
    )
    G.nodes['aldleafPlant_watered']['properties'] = dict(
        name='Aldleaf Plant (Watered)',
        itemCategory='hide',
        cloneFrom='aldleafPlant',
        special='dontCloneReactions',
        description='It will mature in 7 days.',
    )
    G.nodes['aldleafBush']['properties'] = dict(
        cloneFrom='aldleafBush',
        special='dontCloneReactions',
        description='It will produce fruit in 7 days if watered.',
    )
    G.nodes['aldleafBush_wither']['properties'] = dict(
        cloneFrom='aldleafBush_wither',
        special='dontCloneReactions'
    )
    G.nodes['aldleafBush_watered']['properties'] = dict(
        name='Aldleaf Bush (Watered)',
        itemCategory='hide',
        cloneFrom='aldleafBush',
        special='dontCloneReactions',
        description='It will produce fruit in 7 days.',
    )

    return graph_to_plants(expand_graph(G))

def expand_graph(G):
    to_remove = []
    to_add = []
    nodes = []
    for e in G.edges:
        edge = G.edges[e]
        if edge['element'] == 'newDay':
            if 'count' not in edge:
                continue
            element_targets = edge.get('element_targets', {})
            to_remove.append(e)
            head, tail, _ = e
            first = head

            if 'description' in edge:
                days = edge['count']
                s = 's' if days != 1 else ''
                G.nodes[head]['properties']['description'] = edge['description'].format(days=days, s=s)

            for x in range(1, edge['count']):
                last = first + '_'
                properties = {
                    'cloneFrom': first,
                    'special': 'dontCloneReactions',
                    'itemCategory': 'hide'
                }
                if 'description' in edge:
                    days = edge['count'] - x
                    s = 's' if days != 1 else ''
                    properties['description'] = edge['description'].format(days=days, s=s)
                nodes.append((last, properties))
                to_add.append({'__first__': first, '__last__': last, 'element': 'newDay'})
                first = last

                for element, target in element_targets.items():
                    to_add.append({'__first__': first, '__last__': target, 'element': element})

            to_add.append({'__first__': first, '__last__': tail, 'element': 'newDay'})
            spawnItem = edge.get('spawnItem', None)
            if spawnItem:
                to_add[-1]['spawnItem'] = spawnItem

    for e in to_remove:
        G.remove_edge(*e)

    for e in to_add:
        first = e.pop('__first__')
        last = e.pop('__last__')
        G.add_edge(first, last, **e)

    for n, p in nodes:
        G.nodes[n]['properties'] = p

    return G

def graph_to_plants(G):
    items = []
    for node in G:
        if node == 'X':
            continue

        reactions = []
        for tail in G[node]:
            edge = G[node][tail][0]
            element = edge['element']
            spawnItem = edge.get('spawnItem', None)
            action = edge.get('action', None)
            r = ItemReaction(element, newID=tail, spawnItem=spawnItem, action=action)
            reactions.append(r)
        ItemType(node, reactions=reactions, **G.nodes[node].get('properties', {}))

def write_dot(G, filename):
    for e in G.edges:
        edge = G.edges[e]
        edge['label'] = edge.pop('element')
    return _write_dot(G, filename)

def define_plants():
    with collect_records() as c:
        define_turnip()
        return c

if __name__ == '__main__':
    print(define_plants().serialize())
