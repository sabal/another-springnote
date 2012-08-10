jQuery(function () {
    jQuery('#sb__index__tree')
        .jstree({
            'plugins': [
                'crrm',
                'dnd',
                'html_data',
                'themes',
                'ui',
            ]
        })
        .bind('move_node.jstree', function (e, data) {
            data.rslt.o.each(function (i) {
                // TODO: alphabetize
                jQuery.ajax({
                    async: false,
                    type: 'POST',
                    url: DOKU_BASE + 'lib/plugins/sabal/ajax.php',
                    data: {
                        'action': 'move',
                        'id': jQuery(this).attr('id').replace('node_', ''),
                        'parent': data.rslt.np.attr('id').replace('node_', ''),
                    },
                    success: function (r) {
                        if (! r.status)
                            jQuery.jstree.rollback(data.rlbk);
                        else {
                        };
                    },
                });
            });
        });
});
