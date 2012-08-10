<?php

// must be run within Dokuwiki
if (!defined('DOKU_INC')) die();

if (!defined('DOKU_LF')) define('DOKU_LF', "\n");
if (!defined('DOKU_TAB')) define('DOKU_TAB', "\t");
if (!defined('DOKU_PLUGIN')) define('DOKU_PLUGIN',DOKU_INC.'lib/plugins/');

require_once DOKU_PLUGIN.'action.php';

class action_plugin_sabal extends DokuWiki_Action_Plugin {

    public function register(Doku_Event_Handler &$controller) {
        $controller->register_hook('TPL_METAHEADER_OUTPUT', 'BEFORE', $this,
            'handle_tpl_metaheader_output');
    }

    public function handle_tpl_metaheader_output(Doku_Event &$event, $param) {
        $event->data['script'][] = array (
            'type' => 'text/javascript',
            'charset' => 'utf-8',
            'src' => DOKU_BASE."lib/plugins/sabal/jquery.jstree.js",
            '_data' => '',
        );
    }
}

?>
