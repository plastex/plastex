//
// This code fixes up the images so that MSIE doesn't truncate images
// within tables.  It also adjusts the line height so that it's prettier.
//
var images = document.getElementsByTagName('img')
var adjusted = new Array();
for ( var i = 0; i < images.length; i++ )
{
    image = images[i];
    if ( parseInt(image.style.marginBottom) < -8 )
    {
        if ( !image.height )
            continue;

        // Make sure that images in IE in tables don't get truncated
        ieimgfix = document.createElement('img');
        ieimgfix.src = 'iicons/blank.gif';
        ieimgfix.style.height = image.style.height;
        ieimgfix.style.width = '0px';

        // Adjust line height to be prettier
        adjust = document.createElement('span');
        adjust.style.lineHeight = (parseInt(image.style.height) - 8) + 'px';
        adjust.style.visibility = 'hidden';
        adjust.nodeValue = '&8205;';

        // Store away the nodes for use later
        adjusted[image.parentNode] = new Array(image.parentNode, image,
                                               ieimgfix, adjust);
    }
}
// Insert the adjuster nodes
for ( var n in adjusted )
{
    adjusted[n][0].insertBefore(adjusted[n][2], adjusted[n][1]);
    adjusted[n][0].insertBefore(adjusted[n][3], adjusted[n][1]);
}
