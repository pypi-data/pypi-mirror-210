require_relative 'abstract_command_handler'

class ArrayHandler < AbstractCommandHandler
  def process(command)
    begin
      array = command.payload.slice(1..-1)
      return array
    rescue Exception => e
      return e
    end
  end
end