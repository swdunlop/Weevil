%stylesheets=[
% '/s/dark-hive/jquery-ui-1.8.1.custom.css',
% '/s/weevil.css',
%]
%libs = [
% '/s/jquery/jquery-1.4.2.min.js',
% '/s/jquery/jquery-ui-1.8.1.custom.min.js',
% '/s/core.js'
%]
<?xml version='1.0'?>
<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Strict//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd'>
<html><head>
<title>{{title or 'Weevil'}}</title>
%for css in stylesheets:
<link href="{{css}}" type="text/css" rel="stylesheet"></link>
%end
%for j in libs:
<script type='text/javascript' src='{{j}}'></script>
%end
%for j in js:
<script type='text/javascript' src='/s/{{j}}'></script>
%end
</head><body>
