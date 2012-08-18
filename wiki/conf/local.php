<?php

$conf['title'] = 'DokuWiki on a Stick';
$conf['lang'] = 'ko';
$conf['template'] = 'dokubook';
$conf['useacl'] = 1;
$conf['autopasswd'] = 0;
$conf['superuser'] = '@admin';
$conf['userewrite'] = '0';
$conf['useslash'] = 1;
$conf['useheading'] = 1;  // use meta['title']

$conf['compress'] = 0;

@include(DOKU_CONF.'local.protected.php');

?>
