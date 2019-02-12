from string import Template
from parameters import Parameters as P

generic_pic_template = f'''\
<a href="${{imgpath}}/${{hash}}_${{type}}.{P.plot_format}">
<img alt="$hash" src="${{imgpath}}/${{hash}}_${{type}}.{P.plot_format}" width="{P.image_width}" />
</a>'''

opendiv = '<div class="single_hash">'
closediv = '</div>'

generic_singlepic_template = Template(opendiv + generic_pic_template + closediv)

generic_doublepic_template = Template(
    opendiv +
    '\n<table><tr><td class="invis">\n' +
    Template(generic_pic_template).safe_substitute(type='${type1}') +
    '\n</td><td class="invis">\n' +
    Template(generic_pic_template).safe_substitute(type='${type2}') +
    '\n</td></tr></table>\n' +
    closediv
    )

full_template = Template(
    opendiv +
    '\n<table><tr><td class="invis">\n' +
    Template(generic_pic_template).safe_substitute(type='phi') +
    '\n</td><td class="invis">\n' +
    Template(generic_pic_template).safe_substitute(type='theta') +
    '\n</td></tr><tr><td class="invis">\n' +
    Template(generic_pic_template).safe_substitute(type='phi3x3') +
    '\n</td><td class="invis">\n' +
    Template(generic_pic_template).safe_substitute(type='theta3x3') +
    '\n</td></tr></table>\n' +
    closediv
    )

veryfull_template = Template(
    opendiv +
    '\n<table><tr><td class="invis">\n' +
    Template(generic_pic_template).safe_substitute(type='energy') +
    '\n</td><td class="invis">\n' +
    Template(generic_pic_template).safe_substitute(type='steps') +
    '\n</td></tr><tr><td class="invis">\n' +
    Template(generic_pic_template).safe_substitute(type='phi') +
    '\n</td><td class="invis">\n' +
    Template(generic_pic_template).safe_substitute(type='theta') +
    '\n</td></tr><tr><td class="invis">\n' +
    Template(generic_pic_template).safe_substitute(type='phi3x3') +
    '\n</td><td class="invis">\n' +
    Template(generic_pic_template).safe_substitute(type='theta3x3') +
    '\n</td></tr></table>\n' +
    closediv
    )

image_templates = {
    'energy' :
        Template(generic_singlepic_template.safe_substitute(type='energy')),
    'steps' :
        Template(generic_singlepic_template.safe_substitute(type='steps')),

    'phi' :
        Template(generic_singlepic_template.safe_substitute(type='phi')),
    'theta' :
        Template(generic_singlepic_template.safe_substitute(type='theta')),
    'phi3x3' :
        Template(generic_singlepic_template.safe_substitute(type='phi3x3')),
    'theta3x3' :
        Template(generic_singlepic_template.safe_substitute(type='theta3x3')),

    'phi+theta' :
        Template(generic_doublepic_template.safe_substitute(type1='phi', type2='theta')),
    'phi3x3+theta3x3' :
        Template(generic_doublepic_template.safe_substitute(type1='phi3x3', type2='theta3x3')),

    'full' :
        full_template,
    'veryfull' :
        veryfull_template
}

if __name__ == '__main__':
    from pprint import pprint

    for k in image_templates:
        try:
            image_templates[k] = image_templates[k].safe_substitute(hash='${hash}')
        except:
            print(k, 'raised exception')

    pprint(image_templates)
