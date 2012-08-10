<?php

if(!defined('DOKU_INC'))
    define('DOKU_INC',dirname(__FILE__).'/../../../');
require_once(DOKU_INC.'inc/init.php');
//close session
session_write_close();

// TODO: ACL
$ACT = $_REQUEST['action'];
$fn = 'ajax_'.$ACT;

if (function_exists($fn)) {
    $result = $fn();
    if ($result) {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode($result);
    }
}

function ajax_move() {
    global $conf;
    $ID = getID();
    $PARENT = $_REQUEST['parent'];
    $XML_PATH = $conf['metadir'].'/_tree.xml';

    // TODO: ACL

    $xml = new SimpleXMLIterator($XML_PATH, 0, true);
    $node = null;
    $new_parent = null;
    foreach ($xml->page as $page) {
        if ($page['id'] == $ID) {
            $node = dom_import_simplexml($page);
        } elseif ($page['id'] == $PARENT) {
            $new_parent = dom_import_simplexml($page);
        }
    }
    $result = Array(
        'status' => 0
    );
    if (! $node || ! $new_parent)
        return $result;
    $node->parentNode->removeChild($node);
    $new_parent->appendChild($node);
    $xml->asXML($XML_PATH);
    $result['status'] = 1;
    return $result;
}

?>
