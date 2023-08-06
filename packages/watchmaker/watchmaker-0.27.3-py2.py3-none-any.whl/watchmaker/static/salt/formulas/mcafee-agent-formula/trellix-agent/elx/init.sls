#
# This salt state installs Trellix Agent dependencies, configures iptables, and
# runs a downloaded copy of ePO server's exported install.sh. The `install.sh`
# file is a pre-configured, self-installing SHell ARchive. The SHAR installs
# the MFEcma and MFErt RPMs, service configuration (XML) files and SSL keys
# necessary to secure communications between the local Trellix agent software
# and the ePO server.
#
#################################################################
{%- from tpldir ~ '/map.jinja' import trellix with context %}

Install Trellix Agent Dependencies:
  pkg.installed:
    - pkgs:
      - unzip
      - ed

{%- for port in trellix.client_in_ports %}
  {%- if salt.grains.get('osmajorrelease') == 7 %}
    {%- for zone in salt.firewalld.get_zones() %}
Allow ePO Mgmt Inbound Port {{ port }}-{{ zone }}:
  module.run:
    - name: 'firewalld.add_port'
    - zone: '{{ zone }}'
    - port: '{{ port }}/tcp'
    - permanent: True
    - require_in:
      - module: Reload firewalld for Trellix Inbound Port {{ port }}
    {%- endfor %}
Reload firewalld for Trellix Inbound Port {{ port }}:
  module.run:
    - name: firewalld.reload_rules
  {%- elif salt.grains.get('osmajorrelease') == 6 %}
Allow ePO Mgmt Inbound Port {{ port }}:
  iptables.append:
    - table: filter
    - chain: INPUT
    - jump: ACCEPT
    - match:
        - state
        - comment
    - comment: "ePO management of Trellix Agent"
    - connstate: NEW
    - dport: {{ port }}
    - proto: tcp
    - save: True
    - require_in:
      - file: Stage Trellix Install Archive
  {%- endif %}
{%- endfor %}

Stage Trellix Install Archive:
  file.managed:
  - name: /root/install.sh
  - source: {{ trellix.source }}
  - source_hash: {{ trellix.source_hash }}
  - user: root
  - group: root
  - mode: 0700
  - show_changes: False
  - require:
    - pkg: Install Trellix Agent Dependencies

Remove Existing Packages:
  pkg.purged:
    - pkgs: {{ trellix.rpms }}

Install Trellix Agent:
  cmd.run:
    - name: 'sh /root/install.sh {{ trellix.installer_opts }}'
    - cwd: '/root'
    - require:
      - file: Stage Trellix Install Archive
      - pkg: Remove Existing Packages
