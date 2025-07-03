-- mermaid.lua
function CodeBlock(el)
  if el.classes:includes("mermaid") then
    return pandoc.RawBlock("html", '<pre class="mermaid">\n' .. el.text .. '\n</pre>')
  end
end
