%include header title=title, js=['search_tree.js']
<table>
%for row in rows:
{{!row}}
%end
</table>
%include footer
