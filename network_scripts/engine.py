from jinja2 import Template


def gerar_script(unidade, template_obj):
    template = Template(template_obj.template)

    link = unidade.link

    script = template.render(
        hostname=unidade.hostname,
        cidade=unidade.cidade,
        uf=unidade.uf,
        vel_mpls=link.velocidade_mpls,
        vel_internet=link.velocidade_internet,
        ip_mpls=link.ip_mpls,
        ip_fortigate=link.ip_fortigate,
        mask=link.mask,
        vlan_id=link.vlan_id,
    )

    return script