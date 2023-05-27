//
// Created by felix on 20.04.23.
//

#ifndef SRC_DOCSTRINGFORMAT_HPP
#define SRC_DOCSTRINGFORMAT_HPP


#include <string>
#include <vector>
#include <sstream>
#include <algorithm>
#include <iostream>

const std::string PY_TAB = "    ";

auto replaceAll = [](std::string& str_, const std::string& original, const std::string& new_){
    while(str_.find(original) != std::string::npos)
    {
        str_.replace(str_.find(original), original.size(), new_);
    }
};

enum class ParameterKind
{
    ARG,
    POS_ONLY,
    KW_ONLY,
    VARIADIC_ARG,
    KEYWORD_ARG,
};

enum class DocstringFormatStyle
{
    reST,
    GOOGLE,
    NUMPY
};

ParameterKind from_str(const std::string &kind)
{
    if (kind == "Argument")
    {
        return ParameterKind::ARG;
    }
    else if (kind == "Positional only argument")
    {
        return ParameterKind::POS_ONLY;
    }
    else if (kind == "Keyword only argument")
    {
        return ParameterKind::KW_ONLY;
    }
    else if (kind == "Variadic arguments")
    {
        return ParameterKind::VARIADIC_ARG;
    }
    else if (kind == "Keyword arguments")
    {
        return ParameterKind::KEYWORD_ARG;
    }
    
    return ParameterKind::ARG;
}

std::ostream& operator<<(std::ostream &out, ParameterKind const &obj) noexcept
{
    switch (obj)
    {
        case ParameterKind::ARG:
            return out << "Argument";
        case ParameterKind::POS_ONLY:
            return out << "Positional only argument";
        case ParameterKind::KW_ONLY:
            return out << "Keyword only argument";
        case ParameterKind::VARIADIC_ARG:
            return out << "Variadic arguments";
        case ParameterKind::KEYWORD_ARG:
            return out << "Keyword arguments";
    }
    
    return out;
}

std::string remove_trailing_whitespace(std::string &txt)
{
    // remove trailing whitespaces
    for (size_t idx = txt.size() - 1; idx > 0; --idx)
    {
        if (!std::isspace(txt[idx]))
        {
            return txt.substr(0, idx + 1);
        }
    }
    
    return "";
}

std::string remove_whitespace(const std::string &txt)
{
    // remove prefix whitespaces
    for (size_t idx = 0; idx < txt.size(); ++idx)
    {
        if (!std::isspace(txt[idx]))
        {
            return txt.substr(idx);
        }
    }
    
    return "";
}

struct FunctionParameter
{
    std::string name;
    std::string default_value;
    std::string type;
    ParameterKind kind;
    uint line_no;
    std::string description;
    
    void update_description(const std::string &descr, DocstringFormatStyle &formatStyle)
    {
        switch (formatStyle)
        {
            case DocstringFormatStyle::reST:
                update_rest_description(descr);
                break;
            case DocstringFormatStyle::GOOGLE:
            case DocstringFormatStyle::NUMPY:
                update_description(descr);
                break;
        }
    }
    
    void update_description(const std::string &descr)
    {
        std::stringstream sstream;
        sstream << kind;
    
        auto kind_name = sstream.str();
        auto start_pos = descr.find(kind_name) + kind_name.size() + 2;
        auto end_pos = descr.size();
    
        if (!default_value.empty())
        {
            end_pos = descr.find("default") - 2;
        }
    
        auto new_description = descr.substr(start_pos, end_pos - start_pos);
    
        description = remove_trailing_whitespace(new_description);
    }
    
    void update_rest_description(const std::string &descr)
    {
        std::stringstream sstream;
        
        auto param_name = ":param " + name + ":";
        auto type_param = ":type " + name + ":";
        auto kind_param = ":kind " + name + ":";
        auto start_pos = descr.find(param_name) + param_name.size();
        size_t end_pos = 0;
        
        if (!default_value.empty())
        {
            end_pos = descr.find("(default is") - 2;
        }
        else if (!type.empty())
        {
            end_pos = descr.find(type_param) - 2;
        }
        else
        {
            end_pos = descr.find(kind_param) - 2;
        }
        
        if ((end_pos + 2) < std::string::npos)
        {
            auto new_description = descr.substr(start_pos, end_pos - start_pos);
            description = remove_whitespace(remove_trailing_whitespace(new_description));
        }
    }
};

struct FunctionReturn
{
    std::string type;
    uint line_no;
    std::string description;
};

struct FunctionDocstring
{
    std::string docstring;
    uint start_line;
    uint end_line;
};

struct FunctionInfo
{
    uint offset;
    std::string name;
    FunctionDocstring docstring;
    FunctionReturn returns;
    std::vector<FunctionParameter> args {};
    
    int get_file_write_position()
    {
        if (!docstring.docstring.empty())
        {
            return docstring.start_line;
        }
        
        if (returns.line_no > 0)
        {
            return static_cast<int>(returns.line_no + 1);
        }
        else if (!args.empty())
        {
            return static_cast<int>(args[args.size() - 1].line_no + 1);
        }
        
        return 0;
    }
    
    void update_descriptions(DocstringFormatStyle &formatStyle)
    {
        for (int idx = 0; idx < args.size(); ++idx)
        {
            size_t start_pos;
            
            if (formatStyle == DocstringFormatStyle::reST)
            {
                start_pos = docstring.docstring.find(":param " + args[idx].name + ":");
            }
            else
            {
                start_pos = docstring.docstring.find(args[idx].name);
            }
            
            if (start_pos < std::string::npos)
            {
                uint end_pos = docstring.docstring.size() - 1;
                
                if (idx < args.size() - 1)
                {
                    end_pos = docstring.docstring.find(args[idx + 1].name);
                }
                else if (idx == args.size() - 1 && docstring.docstring.find("Returns") < std::string::npos)
                {
                    end_pos = docstring.docstring.find("Returns") - 1;
                }
                
                std::string part_of_interest = docstring.docstring.substr(start_pos, end_pos - start_pos);
                args[idx].update_description(part_of_interest, formatStyle);
            }
        }
    }
};

struct DocstringFormat
{
    FunctionInfo functionInfo;
    
    virtual std::string docstringArgs() noexcept = 0;
    virtual std::string docstringReturn() noexcept = 0;
    
    virtual void check_current_docstring() noexcept = 0;
    
    virtual ~DocstringFormat() = default;
    
    [[ nodiscard ]] std::string docstring() noexcept
    {
        std::stringstream sstream;
        auto current_pytab = get_tabs();
    
        sstream << current_pytab << R"(""")";
        if (functionInfo.docstring.docstring.empty())
        {
            sstream << "\n";
        }
        sstream << docstringArgs();
        sstream << docstringReturn();
        
        sstream << current_pytab << R"(""")";
        if (functionInfo.docstring.docstring.empty())
        {
            sstream << "\n";
        }
        
        return sstream.str();
    }
    
    [[ nodiscard ]] std::string get_tabs() noexcept
    {
        auto current_py_tab = PY_TAB;
        for (uint idx = 0; idx < (functionInfo.offset / 4); ++idx)
        {
            current_py_tab += PY_TAB;
        }
        
        return current_py_tab;
    }
};

struct GoogleDocstring : DocstringFormat
{
    void check_current_docstring() noexcept override
    {
        auto current_py_tab = get_tabs();
        auto google_args_begin = functionInfo.docstring.docstring.find("Args:");
        
        if (google_args_begin < std::string::npos)
        {
            functionInfo.docstring.docstring = functionInfo.docstring.docstring.substr(0, google_args_begin - (current_py_tab.size() + 1));
            functionInfo.docstring.end_line = functionInfo.docstring.start_line + google_args_begin;
        }
    }
    
    std::string docstringArgs() noexcept override
    {
        std::stringstream sstream;
        auto current_py_tab = get_tabs();
        
        if (!functionInfo.docstring.docstring.empty())
        {
            sstream << functionInfo.docstring.docstring;
            sstream << "\n";
        }
        
        if (PY_TAB != current_py_tab)
        {
            sstream << current_py_tab;
            current_py_tab += PY_TAB;
        }
        else
        {
            sstream << PY_TAB;
            current_py_tab = PY_TAB + PY_TAB;
        }
        
        sstream << "Args:\n";
        std::for_each(functionInfo.args.begin(), functionInfo.args.end(),
                      [&sstream, &current_py_tab](const FunctionParameter &val){
            sstream << current_py_tab << val.name;
            if (!val.type.empty())
            {
                sstream << " (" << val.type;
                if (!val.default_value.empty())
                {
                    sstream << ", optional";
                }
                sstream << ")";
            }
            
            if (val.description.empty())
            {
                sstream << " : " << val.kind << "\n";
            }
            else
            {
                sstream << " : " << val.kind  << ". " << val.description << "\n";
            }
            
            if (!val.default_value.empty())
            {
                sstream << current_py_tab << PY_TAB << "(default is " << val.default_value << ")\n";
            }
        });
        
        return sstream.str();
    }
    
    std::string docstringReturn() noexcept override
    {
        std::stringstream sstream;
        auto current_py_tab = get_tabs();
        
        sstream << "\n";
        
        if (!functionInfo.returns.description.empty() || !functionInfo.returns.type.empty())
        {
            if (PY_TAB != current_py_tab)
            {
                sstream << PY_TAB;
            }
            else
            {
                sstream << PY_TAB;
                current_py_tab = PY_TAB + PY_TAB;
            }
            
            sstream << "Returns:\n";
            sstream << current_py_tab;
            if (!functionInfo.returns.type.empty())
            {
                sstream << "( " << functionInfo.returns.type << " ) : ";
            }
            sstream << functionInfo.returns.description << "\n";
    
            sstream << "\n";
        }
        
        return sstream.str();
    }
};

struct reStructuredDocstring : DocstringFormat
{
    void check_current_docstring() noexcept override
    {
        auto current_py_tab = get_tabs();
        auto rest_args_begin = functionInfo.docstring.docstring.find(":param");
    
        if (rest_args_begin < std::string::npos)
        {
            functionInfo.docstring.docstring = functionInfo.docstring.docstring.substr(0, rest_args_begin - (current_py_tab.size() + 1));
            functionInfo.docstring.end_line = functionInfo.docstring.start_line + rest_args_begin;
        }
    }
    
    std::string docstringArgs() noexcept override
    {
        std::stringstream docstream;
    
        auto current_py_tab = get_tabs();
    
        if (!functionInfo.docstring.docstring.empty())
        {
            docstream << functionInfo.docstring.docstring;
            docstream << "\n";
        }
        
        std::for_each(functionInfo.args.begin(), functionInfo.args.end(),
                    [&docstream, &current_py_tab](const FunctionParameter &val)
        {
    
            docstream << current_py_tab << ":param " << val.name << ":";
             
             if (!val.description.empty())
             {
                 docstream << " " << val.description;
             }
             
             docstream << "\n";
            
             if (!val.default_value.empty())
            {
                docstream << current_py_tab << PY_TAB << "(default is " << val.default_value << ")\n";
            }
             
             if (!val.type.empty())
             {
                 docstream << current_py_tab << ":type " << val.name << ": " << val.type;
                 if (!val.default_value.empty())
                 {
                     docstream << ", optional";
                 }
                 
                 docstream << "\n";
             }
             else if (val.type.empty() && !val.default_value.empty())
             {
                 docstream << current_py_tab << ":type " << val.name << ": optional\n";
             }
    
            docstream << current_py_tab << ":kind " << val.name << ": " << val.kind << "\n";

        });
        
        return docstream.str();
    }
    
    std::string docstringReturn() noexcept override
    {
        std::stringstream sstream;
    
        auto current_py_tab = get_tabs();
        
        if (!functionInfo.returns.description.empty())
        {
            sstream << current_py_tab << ":returns:" << functionInfo.returns.description << "\n";
        }
        if (!functionInfo.returns.type.empty())
        {
            sstream << current_py_tab << ":rtype:" << functionInfo.returns.type << "\n";
        }
        return sstream.str();
    }
};

struct NumpyDocstring : DocstringFormat
{
    void check_current_docstring() noexcept override
    {
        auto current_py_tab = get_tabs();
        auto numpy_args_begin = functionInfo.docstring.docstring.find("Parameters");
        
        if (numpy_args_begin < std::string::npos)
        {
            functionInfo.docstring.docstring = functionInfo.docstring.docstring.substr(0, numpy_args_begin - (current_py_tab.size() + 1));
            functionInfo.docstring.end_line = functionInfo.docstring.start_line + numpy_args_begin;
        }
    }
    
    std::string docstringArgs() noexcept override
    {
        std::stringstream docstream;
        auto current_py_tab = get_tabs();
    
        if (!functionInfo.docstring.docstring.empty())
        {
            docstream << functionInfo.docstring.docstring;
            docstream << "\n";
        }
    
        docstream << current_py_tab << "Parameters\n";
        docstream << current_py_tab << "----------\n";
        std::for_each(functionInfo.args.begin(), functionInfo.args.end(),
                      [&docstream, &current_py_tab](const FunctionParameter &val)
        {
            std::stringstream sstream;
            
            sstream << current_py_tab << val.name;
            sstream << " :" ;
            
            if (!val.type.empty())
            {
              sstream << " " << val.type;
              
              if (!val.default_value.empty())
              {
                  sstream << ", optional";
              }
            }
            
            if (!val.default_value.empty())
            {
                if (!val.type.empty())
                {
                    sstream << ", ";
                }
                sstream << "default: " << val.default_value;
            }
            
            sstream << " [" << val.kind << "]";
            
            if (!val.description.empty())
            {
                sstream << "\n";
                sstream << current_py_tab << PY_TAB << remove_whitespace(val.description);
            }
    
            auto docstring = sstream.str();
            docstring = remove_trailing_whitespace(docstring);
            
            docstream << docstring << "\n";
        });
        
        return docstream.str();
    }
    
    std::string docstringReturn() noexcept override
    {
        std::stringstream sstream;
        auto current_py_tab = get_tabs();
    
        if (!functionInfo.returns.type.empty())
        {
            sstream << "\n";
            sstream << current_py_tab << "Returns\n";
            sstream << current_py_tab << "-------\n";
            
            sstream << current_py_tab << functionInfo.returns.type;
        }
        
        if (!functionInfo.returns.description.empty())
        {
            sstream << "\n";
            sstream << current_py_tab << PY_TAB << functionInfo.returns.description;
        }
    
        sstream << "\n";
        
        return sstream.str();
    }
};

#endif //SRC_DOCSTRINGFORMAT_HPP
